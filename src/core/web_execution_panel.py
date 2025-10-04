"""
Web-based Interactive Code Execution Panel.
Provides a modern web interface for code execution with real-time updates.
"""

import json
import asyncio
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

from .models import CodeBlock, ExecutionResult, ExecutionStatus, CodeLanguage, AgentConfig
from ..execution.executor_factory import ExecutorFactory


class WebExecutionState(str, Enum):
    """Web execution states."""
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class WebExecutionRequest:
    """Request for web execution."""
    code: str
    language: str
    session_id: str
    timeout: Optional[int] = None


@dataclass
class WebExecutionResponse:
    """Response from web execution."""
    session_id: str
    status: str
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    error_message: Optional[str] = None
    timestamp: str = ""


class WebExecutionPanel:
    """Web-based interactive code execution panel."""
    
    def __init__(self, config: AgentConfig, host: str = "127.0.0.1", port: int = 5000):
        self.config = config
        self.host = host
        self.port = port
        
        # Flask app setup
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.app.config['SECRET_KEY'] = 'terminal_cli_execution_panel'
        
        # SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Execution state
        self.executor_factory = ExecutorFactory(config)
        self.active_executions: Dict[str, threading.Thread] = {}
        self.execution_history: Dict[str, List[Dict]] = {}
        
        # Setup routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main execution panel page."""
            return render_template('execution_panel.html')
        
        @self.app.route('/api/execute', methods=['POST'])
        def execute_code():
            """Execute code via REST API."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                code = data.get('code', '')
                language = data.get('language', 'python')
                session_id = data.get('session_id', str(uuid.uuid4()))
                timeout = data.get('timeout', self.config.max_execution_time)
                
                if not code.strip():
                    return jsonify({'error': 'No code provided'}), 400
                
                # Create code block
                try:
                    lang_enum = CodeLanguage(language)
                except ValueError:
                    lang_enum = CodeLanguage.PYTHON
                
                code_block = CodeBlock(
                    content=code,
                    language=lang_enum
                )
                
                # Execute code
                result = self._execute_code_sync(code_block, timeout)
                
                # Create response
                response = WebExecutionResponse(
                    session_id=session_id,
                    status=result.status.value,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=result.execution_time,
                    error_message=result.error_message,
                    timestamp=datetime.now().isoformat()
                )
                
                return jsonify(asdict(response))
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/languages', methods=['GET'])
        def get_languages():
            """Get available programming languages."""
            executor = self.executor_factory.create_executor()
            if hasattr(executor, 'get_available_languages'):
                languages = executor.get_available_languages()
            else:
                languages = ["python", "javascript", "typescript", "java", "cpp", "rust", "go"]
            
            return jsonify({'languages': languages})
        
        @self.app.route('/api/history/<session_id>', methods=['GET'])
        def get_history(session_id: str):
            """Get execution history for a session."""
            history = self.execution_history.get(session_id, [])
            return jsonify({'history': history})
        
        @self.app.route('/api/stop/<session_id>', methods=['POST'])
        def stop_execution(session_id: str):
            """Stop execution for a session."""
            if session_id in self.active_executions:
                # Signal the thread to stop
                thread = self.active_executions[session_id]
                if thread.is_alive():
                    # Note: This is a simplified stop mechanism
                    # In production, you'd want more sophisticated process management
                    del self.active_executions[session_id]
                    return jsonify({'status': 'stopped'})
            
            return jsonify({'error': 'No active execution found'}), 404
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            session_id = str(uuid.uuid4())
            join_room(session_id)
            emit('connected', {'session_id': session_id})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            # Clean up any active executions for this session
            pass
        
        @self.socketio.on('execute_code')
        def handle_execute_code(data):
            """Handle code execution request."""
            try:
                code = data.get('code', '')
                language = data.get('language', 'python')
                session_id = data.get('session_id', str(uuid.uuid4()))
                timeout = data.get('timeout', self.config.max_execution_time)
                
                if not code.strip():
                    emit('execution_error', {'error': 'No code provided'})
                    return
                
                # Create code block
                try:
                    lang_enum = CodeLanguage(language)
                except ValueError:
                    lang_enum = CodeLanguage.PYTHON
                
                code_block = CodeBlock(
                    content=code,
                    language=lang_enum
                )
                
                # Start execution in separate thread
                execution_thread = threading.Thread(
                    target=self._execute_code_async,
                    args=(code_block, session_id, timeout)
                )
                execution_thread.daemon = True
                execution_thread.start()
                
                self.active_executions[session_id] = execution_thread
                
                emit('execution_started', {'session_id': session_id})
                
            except Exception as e:
                emit('execution_error', {'error': str(e)})
        
        @self.socketio.on('stop_execution')
        def handle_stop_execution(data):
            """Handle stop execution request."""
            session_id = data.get('session_id')
            if session_id in self.active_executions:
                del self.active_executions[session_id]
                emit('execution_stopped', {'session_id': session_id})
            else:
                emit('execution_error', {'error': 'No active execution found'})
    
    def _execute_code_sync(self, code_block: CodeBlock, timeout: int) -> ExecutionResult:
        """Execute code synchronously."""
        executor = self.executor_factory.create_executor()
        return executor.execute_code(code_block, timeout)
    
    def _execute_code_async(self, code_block: CodeBlock, session_id: str, timeout: int):
        """Execute code asynchronously with real-time updates."""
        try:
            # Emit start event
            self.socketio.emit('execution_output', {
                'session_id': session_id,
                'type': 'info',
                'message': f"Running {code_block.language.value} code..."
            })
            
            # Execute code
            executor = self.executor_factory.create_executor()
            result = executor.execute_code(code_block, timeout)
            
            # Emit result
            self.socketio.emit('execution_complete', {
                'session_id': session_id,
                'status': result.status.value,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': result.execution_time,
                'error_message': result.error_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Add to history
            if session_id not in self.execution_history:
                self.execution_history[session_id] = []
            
            history_entry = {
                'code': code_block.content,
                'language': code_block.language.value,
                'status': result.status.value,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': result.execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.execution_history[session_id].append(history_entry)
            
            # Keep history size limit
            if len(self.execution_history[session_id]) > 50:
                self.execution_history[session_id] = self.execution_history[session_id][-50:]
            
        except Exception as e:
            self.socketio.emit('execution_error', {
                'session_id': session_id,
                'error': str(e)
            })
        
        finally:
            # Clean up
            if session_id in self.active_executions:
                del self.active_executions[session_id]
    
    def run(self, debug: bool = False):
        """Run the web execution panel."""
        print(f"🚀 Starting Web Execution Panel at http://{self.host}:{self.port}")
        print("Press Ctrl+C to stop the server")
        
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=debug,
                allow_unsafe_werkzeug=True
            )
        except KeyboardInterrupt:
            print("\n🛑 Web Execution Panel stopped")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        # Stop all active executions
        for session_id in list(self.active_executions.keys()):
            if session_id in self.active_executions:
                del self.active_executions[session_id]
        
        # Cleanup executor factory
        if self.executor_factory:
            self.executor_factory.cleanup_all_executors()


# Convenience function to create and run the web panel
def run_web_execution_panel(config: AgentConfig, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    """Run the web-based execution panel."""
    panel = WebExecutionPanel(config, host, port)
    panel.run(debug)
