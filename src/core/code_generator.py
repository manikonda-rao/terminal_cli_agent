"""
Code generation engine using LLM integration.
"""

import os
import json
from typing import List, Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from .models import Intent, CodeBlock, CodeLanguage, AgentConfig


class CodeGenerator:
    """Generates code based on parsed intents using LLM integration."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize LLM clients based on configuration
        if config.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        elif config.llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = Anthropic(api_key=api_key)
    
    def generate_code(self, intent: Intent, context: Optional[Dict] = None) -> List[CodeBlock]:
        """
        Generate code based on parsed intent.
        
        Args:
            intent: Parsed intent from natural language
            context: Additional context for code generation
            
        Returns:
            List of generated code blocks
        """
        context = context or {}
        
        # Build prompt based on intent type
        prompt = self._build_prompt(intent, context)
        
        # Generate code using LLM
        generated_text = self._call_llm(prompt)
        
        # Parse generated text into code blocks
        code_blocks = self._parse_generated_code(generated_text, intent.language)
        
        return code_blocks
    
    def _build_prompt(self, intent: Intent, context: Dict) -> str:
        """Build prompt for LLM based on intent and context."""
        base_prompt = f"""You are an expert software developer. Generate clean, well-documented code based on the following request:

Request: {intent.original_text}
Intent Type: {intent.type.value}
Language: {intent.language.value if intent.language else 'python'}
Confidence: {intent.confidence}

Parameters: {json.dumps(intent.parameters, indent=2)}

Context: {json.dumps(context, indent=2)}

Please generate code that:
1. Is syntactically correct and follows best practices
2. Includes appropriate comments and documentation
3. Handles edge cases appropriately
4. Is ready to run/test

"""
        
        # Add specific instructions based on intent type
        if intent.type.value == "create_function":
            base_prompt += f"""
Generate a Python function that {intent.parameters.get('description', 'performs the requested operation')}.
- Include proper type hints
- Add docstring with description, parameters, and return value
- Handle common edge cases
- Use descriptive variable names
"""
        
        elif intent.type.value == "create_class":
            base_prompt += f"""
Generate a Python class that {intent.parameters.get('description', 'implements the requested functionality')}.
- Include proper class structure with __init__ method
- Add docstrings for the class and methods
- Include appropriate methods and properties
- Follow Python naming conventions
"""
        
        elif intent.type.value == "modify_code":
            base_prompt += f"""
Modify the existing code to {intent.parameters.get('description', 'implement the requested changes')}.
- Preserve existing functionality where possible
- Make minimal, focused changes
- Update comments and documentation as needed
- Ensure the modified code is still syntactically correct
"""
        
        elif intent.type.value == "run_code":
            base_prompt += f"""
Generate code to test/run the existing function with the following test data: {intent.parameters.get('test_data', 'default test cases')}.
- Include test cases that cover normal and edge cases
- Add print statements to show results
- Handle any potential errors gracefully
"""
        
        base_prompt += "\n\nGenerate only the code, no explanations or markdown formatting."
        
        return base_prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM to generate code."""
        if self.config.llm_provider == "openai" and self.openai_client:
            return self._call_openai(prompt)
        elif self.config.llm_provider == "anthropic" and self.anthropic_client:
            return self._call_anthropic(prompt)
        else:
            # Fallback to mock generation for testing
            return self._mock_generate(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API to generate code."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._mock_generate(prompt)
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API to generate code."""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return self._mock_generate(prompt)
    
    def _mock_generate(self, prompt: str) -> str:
        """Mock code generation for testing when no API keys are available."""
        # Extract intent from prompt
        if "create_function" in prompt.lower():
            if "quicksort" in prompt.lower():
                return '''def quicksort(arr):
    """
    Sort an array using the quicksort algorithm.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        Sorted list
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)'''
            
            elif "empty lists" in prompt.lower():
                return '''def quicksort(arr):
    """
    Sort an array using the quicksort algorithm.
    Handles empty lists and single elements.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        Sorted list
    """
    if not arr or len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)'''
            
            else:
                return '''def generated_function():
    """
    A generated function based on your request.
    
    Returns:
        None
    """
    # TODO: Implement functionality
    pass'''
        
        elif "create_class" in prompt.lower():
            return '''class GeneratedClass:
    """
    A generated class based on your request.
    """
    
    def __init__(self):
        """Initialize the class."""
        pass
    
    def method(self):
        """A sample method."""
        pass'''
        
        elif "run_code" in prompt.lower():
            return '''# Test the quicksort function
test_data = [3, 6, 8, 10, 1, 2, 1]
print(f"Original: {test_data}")
sorted_data = quicksort(test_data)
print(f"Sorted: {sorted_data}")

# Test with empty list
empty_list = []
print(f"Empty list: {quicksort(empty_list)}")

# Test with single element
single = [42]
print(f"Single element: {quicksort(single)}")'''
        
        else:
            return '''# Generated code based on your request
print("Hello, World!")'''
    
    def _parse_generated_code(self, generated_text: str, language: Optional[CodeLanguage]) -> List[CodeBlock]:
        """Parse generated text into code blocks."""
        # Clean up the generated text
        lines = generated_text.strip().split('\n')
        
        # Remove any markdown formatting
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines[-1].strip() == '```':
            lines = lines[:-1]
        
        content = '\n'.join(lines)
        
        # Create a single code block
        code_block = CodeBlock(
            content=content,
            language=language or CodeLanguage.PYTHON,
            metadata={
                "generated_at": "now",
                "source": "llm"
            }
        )
        
        return [code_block]
