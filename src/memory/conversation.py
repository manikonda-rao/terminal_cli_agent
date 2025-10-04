"""
Conversation memory and context management system.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..core.models import ConversationTurn, ProjectState, Intent, AgentConfig


class ConversationMemory:
    """Manages conversation history and context."""
    
    def __init__(self, config: AgentConfig, project_root: str):
        self.config = config
        self.project_root = Path(project_root)
        self.memory_file = self.project_root / ".coding_agent_memory.json"
        self.conversation_history: List[ConversationTurn] = []
        self.project_context: Dict[str, Any] = {}
        
        # Load existing memory
        self._load_memory()
    
    def _load_memory(self):
        """Load conversation memory from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load conversation history
                self.conversation_history = [
                    ConversationTurn(**turn_data) for turn_data in data.get("conversation_history", [])
                ]
                
                # Load project context
                self.project_context = data.get("project_context", {})
                
                print(f"Loaded {len(self.conversation_history)} conversation turns from memory")
                
            except Exception as e:
                print(f"Warning: Could not load conversation memory: {e}")
                self.conversation_history = []
                self.project_context = {}
    
    def _save_memory(self):
        """Save conversation memory to file."""
        try:
            data = {
                "conversation_history": [turn.model_dump() for turn in self.conversation_history],
                "project_context": self.project_context,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Warning: Could not save conversation memory: {e}")
    
    def add_turn(self, turn: ConversationTurn):
        """Add a new conversation turn to memory."""
        self.conversation_history.append(turn)
        
        # Limit conversation history size
        if len(self.conversation_history) > self.config.max_conversation_history:
            self.conversation_history = self.conversation_history[-self.config.max_conversation_history:]
        
        # Update project context
        self._update_project_context(turn)
        
        # Save memory
        self._save_memory()
    
    def _update_project_context(self, turn: ConversationTurn):
        """Update project context based on conversation turn."""
        # Track active files
        for file_op in turn.file_operations:
            if file_op.operation in ["create", "modify"]:
                if "active_files" not in self.project_context:
                    self.project_context["active_files"] = []
                if file_op.filepath not in self.project_context["active_files"]:
                    self.project_context["active_files"].append(file_op.filepath)
            elif file_op.operation == "delete":
                if "active_files" in self.project_context:
                    self.project_context["active_files"] = [
                        f for f in self.project_context["active_files"] 
                        if f != file_op.filepath
                    ]
        
        # Track last generated code
        if turn.generated_code:
            self.project_context["last_generated_code"] = {
                "language": turn.generated_code[0].language.value,
                "content": turn.generated_code[0].content[:200] + "..." if len(turn.generated_code[0].content) > 200 else turn.generated_code[0].content,
                "timestamp": turn.timestamp.isoformat()
            }
        
        # Track execution results
        if turn.execution_result:
            self.project_context["last_execution"] = {
                "status": turn.execution_result.status.value,
                "success": turn.execution_result.status.value == "completed",
                "timestamp": turn.timestamp.isoformat()
            }
    
    def get_recent_context(self, turns: int = 5) -> Dict[str, Any]:
        """Get recent conversation context."""
        recent_turns = self.conversation_history[-turns:] if self.conversation_history else []
        
        context = {
            "recent_turns": len(recent_turns),
            "last_intent": recent_turns[-1].intent.type.value if recent_turns else None,
            "last_success": recent_turns[-1].success if recent_turns else None,
            "active_files": self.project_context.get("active_files", []),
            "last_generated_code": self.project_context.get("last_generated_code"),
            "last_execution": self.project_context.get("last_execution"),
            "conversation_summary": self._generate_conversation_summary(recent_turns)
        }
        
        return context
    
    def _generate_conversation_summary(self, turns: List[ConversationTurn]) -> str:
        """Generate a summary of recent conversation turns."""
        if not turns:
            return "No recent conversation history."
        
        summary_parts = []
        for turn in turns[-3:]:  # Last 3 turns
            intent_desc = f"{turn.intent.type.value}: {turn.intent.parameters.get('description', 'N/A')}"
            status = "✓" if turn.success else "✗"
            summary_parts.append(f"{status} {intent_desc}")
        
        return " | ".join(summary_parts)
    
    def get_context_for_intent(self, intent: Intent) -> Dict[str, Any]:
        """Get relevant context for a specific intent."""
        context = self.get_recent_context()
        
        # Add intent-specific context
        if intent.type.value == "modify_code":
            # Include last generated code for modification
            if self.project_context.get("last_generated_code"):
                context["code_to_modify"] = self.project_context["last_generated_code"]
        
        elif intent.type.value == "run_code":
            # Include last generated code for execution
            if self.project_context.get("last_generated_code"):
                context["code_to_run"] = self.project_context["last_generated_code"]
        
        elif intent.type.value == "explain_code":
            # Include last generated code for explanation
            if self.project_context.get("last_generated_code"):
                context["code_to_explain"] = self.project_context["last_generated_code"]
        
        return context
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.conversation_history = []
        self.project_context = {}
        self._save_memory()
        print("Conversation memory cleared.")
    
    def export_memory(self, filepath: str):
        """Export conversation memory to a file."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            data = {
                "conversation_history": [turn.model_dump() for turn in self.conversation_history],
                "project_context": self.project_context,
                "exported_at": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"Conversation memory exported to {filepath}")
            
        except Exception as e:
            print(f"Error exporting memory: {e}")
    
    def import_memory(self, filepath: str):
        """Import conversation memory from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load conversation history
            self.conversation_history = [
                ConversationTurn(**turn_data) for turn_data in data.get("conversation_history", [])
            ]
            
            # Load project context
            self.project_context = data.get("project_context", {})
            
            # Save to current memory file
            self._save_memory()
            
            print(f"Conversation memory imported from {filepath}")
            
        except Exception as e:
            print(f"Error importing memory: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        if not self.conversation_history:
            return {"total_turns": 0}
        
        total_turns = len(self.conversation_history)
        successful_turns = sum(1 for turn in self.conversation_history if turn.success)
        failed_turns = total_turns - successful_turns
        
        # Count intent types
        intent_counts = {}
        for turn in self.conversation_history:
            intent_type = turn.intent.type.value
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
        
        # Count languages
        language_counts = {}
        for turn in self.conversation_history:
            if turn.generated_code:
                for code_block in turn.generated_code:
                    lang = code_block.language.value
                    language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            "total_turns": total_turns,
            "successful_turns": successful_turns,
            "failed_turns": failed_turns,
            "success_rate": successful_turns / total_turns if total_turns > 0 else 0,
            "intent_counts": intent_counts,
            "language_counts": language_counts,
            "active_files": len(self.project_context.get("active_files", [])),
            "memory_file_size": self.memory_file.stat().st_size if self.memory_file.exists() else 0
        }
