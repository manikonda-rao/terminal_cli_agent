"""
Main coding agent that orchestrates all components.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

from .models import (
    Intent, CodeBlock, ConversationTurn,
    AgentConfig, IntentType, ExecutionStatus, CodeLanguage
)
from .intent_parser import IntentParser
from .code_generator import CodeGenerator
from .file_manager import FileManager
from .ui import ui
from ..execution.executor_factory import ExecutorFactory
from ..execution.sandbox import SandboxExecutor, DockerExecutor
from ..execution.e2b_executor import E2BExecutor, E2BExecutorWithSecurity
from ..execution.multi_language_executor import MultiLanguageExecutor
from ..memory.conversation import ConversationMemory


class CodingAgent:
    """Main coding agent that orchestrates all components."""
    
    def __init__(self, project_root: str = ".",
                 config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.project_root = project_root
        
        # Initialize components
        self.intent_parser = IntentParser()
        self.code_generator = CodeGenerator(self.config)
        self.file_manager = FileManager(project_root)
        
        # Initialize executor factory
        self.executor_factory = ExecutorFactory(self.config)
        self.executor = self.executor_factory.create_executor()
        
        # Initialize multi-language executor for fallback
        self.multi_lang_executor = MultiLanguageExecutor(self.config)
        
        self.memory = ConversationMemory(self.config, project_root)
        
        ui.info(f"Coding Agent initialized in {project_root}")
        ui.info(f"LLM Provider: {self.config.llm_provider}")
        ui.info(f"Model: {self.config.model_name}")
    
    def process_input(self, user_input: str) -> ConversationTurn:
        """
        Process user input and generate appropriate response - streamlined.
        
        Args:
            user_input: Natural language input from user
        
        Returns:
            ConversationTurn with the complete interaction
        """
        # Parse intent
        context = self.memory.get_recent_context()
        intent = self.intent_parser.parse(user_input, context)
        
        # Get context for this specific intent
        intent_context = self.memory.get_context_for_intent(intent)
        
        # Initialize result variables
        code_blocks = []
        execution_result = None
        file_operations = []
        success = True
        error_message = None
        
        try:
            # For most intents, provide direct LLM response
            if intent.type in [IntentType.CREATE_FUNCTION, IntentType.CREATE_CLASS, IntentType.MODIFY_CODE, 
                              IntentType.EXPLAIN_CODE, IntentType.REFACTOR_CODE, IntentType.DEBUG_CODE]:
                
                # Get direct response from LLM
                response_text = self._get_direct_response(user_input, intent, intent_context)
                
                # Create a code block with the response
                response_block = CodeBlock(
                    content=response_text,
                    language=CodeLanguage.PYTHON,  # Default to Python for responses
                    metadata={
                        "type": "direct_response",
                        "intent": intent.type.value,
                        "generated_at": datetime.now().isoformat()
                    }
                )
                code_blocks.append(response_block)
                
            elif intent.type == IntentType.RUN_CODE:
                # Generate test/execution code
                code_blocks = self.code_generator.generate_code(intent, intent_context)
                
                # Execute the code
                for code_block in code_blocks:
                    execution_result = self.executor.execute_code(code_block)
                
            elif intent.type == IntentType.CREATE_FILE:
                filename = intent.parameters.get("description", "new_file.py")
                content = "# New file created by coding agent\n"
                
                file_op = self.file_manager.create_file(filename, content)
                file_operations.append(file_op)
                
            elif intent.type == IntentType.DELETE_FILE:
                filename = intent.parameters.get("description", "")
                if filename:
                    file_op = self.file_manager.delete_file(filename)
                    file_operations.append(file_op)
                else:
                    raise ValueError("No filename specified for deletion")
                
            elif intent.type == IntentType.SEARCH_CODE:
                query = intent.parameters.get("description", "")
                if query:
                    results = self.file_manager.search_in_files(query)
                    ui.display_search_results(results, query)
                
            else:
                # Default: provide direct response
                response_text = self._get_direct_response(user_input, intent, intent_context)
                
                response_block = CodeBlock(
                    content=response_text,
                    language=CodeLanguage.PYTHON,
                    metadata={
                        "type": "direct_response",
                        "intent": intent.type.value,
                        "generated_at": datetime.now().isoformat()
                    }
                )
                code_blocks.append(response_block)
                
        except Exception as e:
            success = False
            error_message = str(e)
            ui.show_clean_error(e, "Agent processing error")
        
        # Create conversation turn
        turn = ConversationTurn(
            user_input=user_input,
            intent=intent,
            generated_code=code_blocks,
            execution_result=execution_result,
            file_operations=file_operations,
            success=success,
            error_message=error_message
        )
        
        # Add to memory
        self.memory.add_turn(turn)
        
        return turn
    
    def _get_direct_response(self, user_input: str, intent: Intent, context: Dict) -> str:
        """Get direct response from LLM instead of generating code."""
        try:
            # Build a conversational prompt
            prompt = f"""You are a helpful coding assistant. The user has asked: "{user_input}"

Intent detected: {intent.type.value}
Context: {json.dumps(context, indent=2)}

Please provide a helpful response. If the user is asking for code, provide the code with explanations.
If they're asking questions, provide clear answers. Be conversational and helpful.

Response:"""

            # Use the code generator's LLM capabilities to get a response
            # We'll create a simple intent for general response
            response_intent = Intent(
                type=IntentType.EXPLAIN_CODE,  # Use explain as a general response type
                original_text=user_input,
                parameters={"description": "Provide helpful response to user query"},
                confidence=1.0
            )
            
            # Generate response using the code generator
            code_blocks = self.code_generator.generate_code(response_intent, context)
            
            if code_blocks:
                return code_blocks[0].content
            else:
                return "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            ui.show_clean_error(e, "Direct response generation")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _determine_filename(self, code_block: CodeBlock, intent: Intent) -> str:
        """Determine appropriate filename for code block."""
        # Check if filename is specified in metadata
        if code_block.filename:
            return code_block.filename
        
        # Generate filename based on intent and content
        if intent.type == IntentType.CREATE_FUNCTION:
            func_name = intent.parameters.get("function_name", "generated_function")
            return f"{func_name}.py"
        elif intent.type == IntentType.CREATE_CLASS:
            class_name = intent.parameters.get("class_name", "GeneratedClass")
            return f"{class_name.lower()}.py"
        elif intent.type == IntentType.MODIFY_CODE:
            # Try to find existing file to modify
            active_files = self.memory.project_context.get("active_files", [])
            if active_files:
                return active_files[-1]  # Modify the most recent file
            return "modified_code.py"
        else:
            # Default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"generated_code_{timestamp}.py"
    
    def rollback_last_operation(self) -> bool:
        """Rollback the last file operation."""
        try:
            last_turn = self.memory.conversation_history[-1] if self.memory.conversation_history else None
            if not last_turn or not last_turn.file_operations:
                ui.warning("No file operations to rollback")
                return False
            
            # Rollback each file operation
            for file_op in reversed(last_turn.file_operations):
                if file_op.backup_path:
                    rollback_op = self.file_manager.rollback_file(file_op.filepath, file_op.backup_path)
                    ui.success(f"Rolled back {file_op.filepath}")
            
            ui.success("Rollback completed successfully")
            return True
            
        except Exception as e:
            ui.show_clean_error(e, "Rollback operation")
            return False
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status."""
        stats = self.memory.get_statistics()
        project_state = self.file_manager.get_project_state()
        
        # Get execution statistics
        execution_stats = {}
        if hasattr(self.executor, 'get_execution_statistics'):
            execution_stats = self.executor.get_execution_statistics()
        
        # Get multi-language executor stats
        multi_lang_stats = self.multi_lang_executor.get_execution_statistics()
        
        return {
            "project_root": self.project_root,
            "active_files": project_state.active_files,
            "conversation_stats": stats,
            "execution_stats": execution_stats,
            "multi_language_stats": multi_lang_stats,
            "supported_languages": self.multi_lang_executor.get_supported_languages(),
            "available_languages": self.multi_lang_executor.get_available_languages(),
            "config": self.config.to_dict()
        }
    
    def clear_project(self):
        """Clear project and reset state."""
        self.memory.clear_memory()
        ui.success("Project cleared and reset")
    
    def export_project(self, export_path: str):
        """Export project with conversation history."""
        try:
            # Export memory
            memory_export = os.path.join(export_path, "conversation_memory.json")
            self.memory.export_memory(memory_export)
            
            # Copy project files
            import shutil
            shutil.copytree(self.project_root, export_path, dirs_exist_ok=True)
            
            ui.success(f"Project exported to {export_path}")
            
        except Exception as e:
            ui.show_clean_error(e, "Project export")
