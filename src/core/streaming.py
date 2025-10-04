"""
Streaming response system for real-time output.
"""

import asyncio
import time
from typing import AsyncGenerator, Generator, Optional, Any, Dict
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
from rich.align import Align
from rich import box


class StreamingResponse:
    """Handles streaming responses for real-time output."""
    
    def __init__(self, console: Console):
        self.console = console
        self.is_streaming = False
        self.current_content = ""
        self.streaming_speed = 0.02  # Delay between characters
    
    def stream_text(self, text: str, title: str = "Response", 
                   show_typing_indicator: bool = True) -> None:
        """Stream text character by character with typing effect."""
        if not text:
            return
        
        self.is_streaming = True
        self.current_content = ""
        
        # Create a panel for the streaming content
        panel_content = Text()
        panel = Panel(
            panel_content,
            title=title,
            border_style="blue",
            expand=False,
            padding=(1, 2)
        )
        
        with Live(panel, console=self.console, refresh_per_second=30) as live:
            for i, char in enumerate(text):
                if not self.is_streaming:
                    break
                
                self.current_content += char
                
                # Update the panel content
                panel_content.append(char)
                panel.renderable = panel_content
                
                # Add typing indicator
                if show_typing_indicator and i < len(text) - 1:
                    typing_indicator = Text("▋", style="blue")
                    panel_content.append(typing_indicator)
                    panel.renderable = panel_content
                
                live.update(panel)
                time.sleep(self.streaming_speed)
                
                # Remove typing indicator
                if show_typing_indicator and i < len(text) - 1:
                    # Create new content without the typing indicator
                    new_content = Text()
                    for j in range(len(self.current_content)):
                        new_content.append(self.current_content[j])
                    panel_content = new_content
                    panel.renderable = panel_content
                    live.update(panel)
        
        self.is_streaming = False
    
    def stream_code(self, code: str, language: str = "python", 
                   title: str = "Generated Code") -> None:
        """Stream code with syntax highlighting."""
        if not code:
            return
        
        self.is_streaming = True
        self.current_content = ""
        
        # Create syntax object for streaming
        syntax = Syntax("", language, theme="monokai", line_numbers=True)
        panel = Panel(
            syntax,
            title=title,
            border_style="green",
            expand=False
        )
        
        with Live(panel, console=self.console, refresh_per_second=30) as live:
            lines = code.split('\n')
            current_code = ""
            
            for line_idx, line in enumerate(lines):
                if not self.is_streaming:
                    break
                
                # Stream line by line
                for char in line:
                    if not self.is_streaming:
                        break
                    
                    current_code += char
                    syntax = Syntax(current_code, language, theme="monokai", line_numbers=True)
                    panel.renderable = syntax
                    live.update(panel)
                    time.sleep(self.streaming_speed)
                
                # Add newline
                if line_idx < len(lines) - 1:
                    current_code += '\n'
                    syntax = Syntax(current_code, language, theme="monokai", line_numbers=True)
                    panel.renderable = syntax
                    live.update(panel)
                    time.sleep(self.streaming_speed * 2)  # Longer pause for newlines
        
        self.is_streaming = False
    
    def stream_with_progress(self, content: str, title: str = "Processing",
                           progress_items: Optional[list] = None) -> None:
        """Stream content with progress indicators."""
        if not content:
            return
        
        self.is_streaming = True
        
        # Create progress text
        progress_text = Text()
        if progress_items:
            for item in progress_items:
                progress_text.append(f"✓ {item}\n", style="green")
        
        # Create main content
        main_content = Text(content)
        
        # Combine progress and content
        combined_content = Text()
        combined_content.append(progress_text)
        combined_content.append("\n")
        combined_content.append(main_content)
        
        panel = Panel(
            combined_content,
            title=title,
            border_style="yellow",
            expand=False,
            padding=(1, 2)
        )
        
        with Live(panel, console=self.console, refresh_per_second=30) as live:
            # First show progress
            if progress_items:
                for i, item in enumerate(progress_items):
                    if not self.is_streaming:
                        break
                    
                    progress_text.append(f"✓ {item}\n", style="green")
                    panel.renderable = progress_text
                    live.update(panel)
                    time.sleep(0.5)
            
            # Then stream main content
            current_content = ""
            for char in content:
                if not self.is_streaming:
                    break
                
                current_content += char
                combined_content = Text()
                combined_content.append(progress_text)
                combined_content.append("\n")
                combined_content.append(current_content)
                
                panel.renderable = combined_content
                live.update(panel)
                time.sleep(self.streaming_speed)
        
        self.is_streaming = False
    
    def stop_streaming(self) -> None:
        """Stop the current streaming operation."""
        self.is_streaming = False
    
    def set_streaming_speed(self, speed: float) -> None:
        """Set the streaming speed (delay between characters)."""
        self.streaming_speed = max(0.001, min(1.0, speed))


class InteractivePrompt:
    """Interactive prompt system with enhanced UX."""
    
    def __init__(self, console: Console):
        self.console = console
        self.suggestions = []
        self.current_suggestion = 0
    
    def show_suggestions(self, suggestions: list, title: str = "Suggestions") -> None:
        """Show interactive suggestions."""
        if not suggestions:
            return
        
        self.suggestions = suggestions
        self.current_suggestion = 0
        
        # Create suggestions panel
        suggestions_text = Text()
        for i, suggestion in enumerate(suggestions):
            if i == self.current_suggestion:
                suggestions_text.append(f"▶ {suggestion}\n", style="bold blue")
            else:
                suggestions_text.append(f"  {suggestion}\n", style="white")
        
        panel = Panel(
            suggestions_text,
            title=title,
            border_style="cyan",
            expand=False,
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def get_next_suggestion(self) -> Optional[str]:
        """Get the next suggestion."""
        if not self.suggestions:
            return None
        
        self.current_suggestion = (self.current_suggestion + 1) % len(self.suggestions)
        return self.suggestions[self.current_suggestion]
    
    def get_previous_suggestion(self) -> Optional[str]:
        """Get the previous suggestion."""
        if not self.suggestions:
            return None
        
        self.current_suggestion = (self.current_suggestion - 1) % len(self.suggestions)
        return self.suggestions[self.current_suggestion]


class SmartCompleter:
    """Smart autocompletion system."""
    
    def __init__(self):
        self.completions = {
            "create": ["function", "class", "file", "variable"],
            "write": ["function", "class", "script", "test"],
            "implement": ["algorithm", "feature", "interface", "method"],
            "modify": ["function", "class", "file", "code"],
            "run": ["code", "test", "script", "function"],
            "test": ["function", "class", "code", "feature"],
            "debug": ["function", "class", "code", "issue"],
            "explain": ["function", "class", "code", "algorithm"],
            "refactor": ["function", "class", "code", "structure"],
            "search": ["function", "class", "variable", "pattern"],
            "delete": ["file", "function", "class", "variable"],
            "python": ["function", "class", "script", "module"],
            "javascript": ["function", "class", "script", "module"],
            "typescript": ["function", "class", "interface", "module"]
        }
    
    def get_completions(self, text: str) -> list:
        """Get completions for the given text."""
        words = text.lower().split()
        if not words:
            return []
        
        last_word = words[-1]
        completions = []
        
        # Get completions based on context
        for word in words[:-1]:
            if word in self.completions:
                completions.extend(self.completions[word])
        
        # Add completions for the last word
        if last_word in self.completions:
            completions.extend(self.completions[last_word])
        
        # Filter and deduplicate
        completions = list(set(completions))
        return completions[:10]  # Limit to 10 suggestions


# Global instances
streaming_response = StreamingResponse(Console())
interactive_prompt = InteractivePrompt(Console())
smart_completer = SmartCompleter()
