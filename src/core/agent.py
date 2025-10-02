"""
Main coding agent that orchestrates all components.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from .models import (
 Intent, CodeBlock, ExecutionResult, ConversationTurn, 
 AgentConfig, IntentType, ExecutionStatus
)
from .intent_parser import IntentParser
from .code_generator import CodeGenerator
from .file_manager import FileManager
from ..execution.sandbox import SandboxExecutor
from ..memory.conversation import ConversationMemory


class CodingAgent:
 """Main coding agent that orchestrates all components."""
 
 def __init__(self, project_root: str = ".", config: Optional[AgentConfig] = None):
 self.config = config or AgentConfig()
 self.project_root = project_root
 
 # Initialize components
 self.intent_parser = IntentParser()
 self.code_generator = CodeGenerator(self.config)
 self.file_manager = FileManager(project_root)
 self.executor = SandboxExecutor(self.config)
 self.memory = ConversationMemory(self.config, project_root)
 
 print(f" Coding Agent initialized in {project_root}")
 print(f" LLM Provider: {self.config.llm_provider}")
 print(f" Model: {self.config.model_name}")
 
 def process_input(self, user_input: str) -> ConversationTurn:
 """
 Process user input and generate appropriate response.
 
 Args:
 user_input: Natural language input from user
 
 Returns:
 ConversationTurn with the complete interaction
 """
 print(f"\n Processing: {user_input}")
 
 # Parse intent
 context = self.memory.get_recent_context()
 intent = self.intent_parser.parse(user_input, context)
 
 print(f" Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
 
 # Get context for this specific intent
 intent_context = self.memory.get_context_for_intent(intent)
 
 # Generate code based on intent
 code_blocks = []
 execution_result = None
 file_operations = []
 success = True
 error_message = None
 
 try:
 if intent.type in [IntentType.CREATE_FUNCTION, IntentType.CREATE_CLASS, IntentType.MODIFY_CODE]:
 code_blocks = self.code_generator.generate_code(intent, intent_context)
 print(f" Generated {len(code_blocks)} code block(s)")
 
 # Save code to file
 for code_block in code_blocks:
 filename = self._determine_filename(code_block, intent)
 file_op = self.file_manager.create_file(filename, code_block.content)
 file_operations.append(file_op)
 print(f" Saved code to {filename}")
 
 elif intent.type == IntentType.RUN_CODE:
 # Generate test/execution code
 code_blocks = self.code_generator.generate_code(intent, intent_context)
 
 # Execute the code
 for code_block in code_blocks:
 execution_result = self.executor.execute_code(code_block)
 print(f" Execution: {execution_result.status.value}")
 
 if execution_result.status == ExecutionStatus.COMPLETED:
 print(f" Output:\n{execution_result.stdout}")
 else:
 print(f" Error: {execution_result.error_message}")
 if execution_result.stderr:
 print(f" Error details:\n{execution_result.stderr}")
 
 elif intent.type == IntentType.CREATE_FILE:
 filename = intent.parameters.get("description", "new_file.py")
 content = "# New file created by coding agent\n"
 file_op = self.file_manager.create_file(filename, content)
 file_operations.append(file_op)
 print(f" Created file: {filename}")
 
 elif intent.type == IntentType.DELETE_FILE:
 filename = intent.parameters.get("description", "")
 if filename:
 file_op = self.file_manager.delete_file(filename)
 file_operations.append(file_op)
 print(f" Deleted file: {filename}")
 else:
 raise ValueError("No filename specified for deletion")
 
 elif intent.type == IntentType.SEARCH_CODE:
 query = intent.parameters.get("description", "")
 if query:
 results = self.file_manager.search_in_files(query)
 print(f" Search results for '{query}':")
 for filepath, matches in results.items():
 print(f" {filepath}:")
 for match in matches[:3]: # Show first 3 matches
 print(f" {match}")
 if len(matches) > 3:
 print(f" ... and {len(matches) - 3} more matches")
 
 elif intent.type == IntentType.EXPLAIN_CODE:
 # Generate explanation
 code_blocks = self.code_generator.generate_code(intent, intent_context)
 print(" Code explanation:")
 for code_block in code_blocks:
 print(code_block.content)
 
 else:
 # Default: generate code
 code_blocks = self.code_generator.generate_code(intent, intent_context)
 print(f" Generated {len(code_blocks)} code block(s)")
 
 except Exception as e:
 success = False
 error_message = str(e)
 print(f" Error: {error_message}")
 
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
 return active_files[-1] # Modify the most recent file
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
 print(" No file operations to rollback")
 return False
 
 # Rollback each file operation
 for file_op in reversed(last_turn.file_operations):
 if file_op.backup_path:
 rollback_op = self.file_manager.rollback_file(file_op.filepath, file_op.backup_path)
 print(f" Rolled back {file_op.filepath}")
 
 print(" Rollback completed successfully")
 return True
 
 except Exception as e:
 print(f" Rollback failed: {e}")
 return False
 
 def get_project_status(self) -> Dict[str, Any]:
 """Get current project status."""
 stats = self.memory.get_statistics()
 project_state = self.file_manager.get_project_state()
 
 return {
 "project_root": self.project_root,
 "active_files": project_state.active_files,
 "conversation_stats": stats,
 "config": self.config.to_dict()
 }
 
 def clear_project(self):
 """Clear project and reset state."""
 self.memory.clear_memory()
 print(" Project cleared and reset")
 
 def export_project(self, export_path: str):
 """Export project with conversation history."""
 try:
 # Export memory
 memory_export = os.path.join(export_path, "conversation_memory.json")
 self.memory.export_memory(memory_export)
 
 # Copy project files
 import shutil
 shutil.copytree(self.project_root, export_path, dirs_exist_ok=True)
 
 print(f"📦 Project exported to {export_path}")
 
 except Exception as e:
 print(f" Export failed: {e}")
 
 def show_help(self):
 """Show help information."""
 help_text = """
 Terminal Coding Agent Help

Available Commands:
 • Create a Python function for [description]
 • Write a class that [description]
 • Modify the last function to [description]
 • Run the last function with [test data]
 • Create a file called [filename]
 • Delete the file [filename]
 • Search for [query]
 • Explain the last function
 • Refactor the last function
 • Debug the last function
 • Test the last function

Special Commands:
 • /help - Show this help
 • /status - Show project status
 • /rollback - Rollback last operation
 • /clear - Clear project
 • /export [path] - Export project
 • /quit - Exit the agent

Examples:
 > Create a Python function for quicksort
 > Modify the last function to handle empty lists
 > Run the last function with [3, 1, 4, 1, 5]
 > Search for "def quicksort"
 """
 print(help_text)
