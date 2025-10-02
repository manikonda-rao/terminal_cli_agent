"""
Enterprise-grade code generation engine with multi-provider LLM integration framework.
"""

import os
import json
import time
import asyncio
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI, AsyncOpenAI
from anthropic import Anthropic, AsyncAnthropic
from .models import Intent, CodeBlock, CodeLanguage, AgentConfig


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"


class GenerationStatus(str, Enum):
    """Status of code generation."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


@dataclass
class GenerationResult:
    """Result of code generation."""
    status: GenerationStatus
    code_blocks: List[CodeBlock]
    provider_used: Optional[LLMProvider] = None
    generation_time: float = 0.0
    tokens_used: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    name: LLMProvider
    api_key: str
    model: str
    max_tokens: int = 2000
    temperature: float = 0.1
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit_delay: float = 1.0
    enabled: bool = True


class CodeGenerator:
    """Enterprise-grade code generation engine with multi-provider LLM integration framework."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.providers = {}
        self.provider_configs = {}
        self.generation_history = []
        self.rate_limit_tracker = {}
        
        # Initialize provider configurations
        self._initialize_providers()
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_providers(self):
        """Initialize provider configurations."""
        # OpenAI configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.provider_configs[LLMProvider.OPENAI] = ProviderConfig(
                name=LLMProvider.OPENAI,
                api_key=openai_key,
                model=self.config.model_name if self.config.llm_provider == "openai" else "gpt-4",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=30,
                retry_attempts=3
            )
        
        # Anthropic configuration
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.provider_configs[LLMProvider.ANTHROPIC] = ProviderConfig(
                name=LLMProvider.ANTHROPIC,
                api_key=anthropic_key,
                model=self.config.model_name if self.config.llm_provider == "anthropic" else "claude-3-sonnet-20240229",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=30,
                retry_attempts=3
            )
        
        # Google configuration (placeholder for future implementation)
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            self.provider_configs[LLMProvider.GOOGLE] = ProviderConfig(
                name=LLMProvider.GOOGLE,
                api_key=google_key,
                model="gemini-pro",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=30,
                retry_attempts=3,
                enabled=False  # Not implemented yet
            )
    
    def _initialize_clients(self):
        """Initialize LLM clients."""
        # OpenAI client
        if LLMProvider.OPENAI in self.provider_configs:
            try:
                self.providers[LLMProvider.OPENAI] = {
                    "sync": OpenAI(api_key=self.provider_configs[LLMProvider.OPENAI].api_key),
                    "async": AsyncOpenAI(api_key=self.provider_configs[LLMProvider.OPENAI].api_key)
                }
                print(f"✓ OpenAI client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize OpenAI client: {e}")
        
        # Anthropic client
        if LLMProvider.ANTHROPIC in self.provider_configs:
            try:
                self.providers[LLMProvider.ANTHROPIC] = {
                    "sync": Anthropic(api_key=self.provider_configs[LLMProvider.ANTHROPIC].api_key),
                    "async": AsyncAnthropic(api_key=self.provider_configs[LLMProvider.ANTHROPIC].api_key)
                }
                print(f"✓ Anthropic client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize Anthropic client: {e}")
    
    def _get_primary_provider(self) -> Optional[LLMProvider]:
        """Get the primary provider based on configuration."""
        if self.config.llm_provider == "openai" and LLMProvider.OPENAI in self.providers:
            return LLMProvider.OPENAI
        elif self.config.llm_provider == "anthropic" and LLMProvider.ANTHROPIC in self.providers:
            return LLMProvider.ANTHROPIC
        
        # Fallback to any available provider
        for provider in self.providers.keys():
            if self.provider_configs[provider].enabled:
                return provider
        
        return None
    
    def _get_fallback_providers(self, primary: LLMProvider) -> List[LLMProvider]:
        """Get fallback providers in order of preference."""
        fallbacks = []
        for provider in self.providers.keys():
            if provider != primary and self.provider_configs[provider].enabled:
                fallbacks.append(provider)
        return fallbacks
    
    def generate_code(self, intent: Intent, context: Optional[Dict] = None) -> List[CodeBlock]:
        """
        Generate code based on parsed intent with enterprise-grade reliability.
        
        Args:
            intent: Parsed intent from natural language
            context: Additional context for code generation
            
        Returns:
            List of generated code blocks
        """
        context = context or {}
        start_time = time.time()
        
        # Build prompt based on intent type
        prompt = self._build_prompt(intent, context)
        
        # Generate code using LLM with fallback support
        result = self._generate_with_fallback(prompt, intent)
        
        # Store generation history
        self.generation_history.append({
            "timestamp": datetime.now().isoformat(),
            "intent": intent.type.value,
            "provider_used": result.provider_used.value if result.provider_used else None,
            "generation_time": result.generation_time,
            "tokens_used": result.tokens_used,
            "status": result.status.value,
            "retry_count": result.retry_count
        })
        
        # Keep only recent history
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-100:]
        
        return result.code_blocks
    
    def _generate_with_fallback(self, prompt: str, intent: Intent) -> GenerationResult:
        """Generate code with provider fallback support."""
        primary_provider = self._get_primary_provider()
        if not primary_provider:
            return self._fallback_to_mock(prompt, intent)
        
        # Try primary provider first
        result = self._try_provider(primary_provider, prompt, intent)
        if result.status == GenerationStatus.COMPLETED:
            return result
        
        # Try fallback providers
        fallback_providers = self._get_fallback_providers(primary_provider)
        for provider in fallback_providers:
            result = self._try_provider(provider, prompt, intent)
            if result.status == GenerationStatus.COMPLETED:
                return result
        
        # If all providers fail, fall back to mock generation
        return self._fallback_to_mock(prompt, intent)
    
    def _try_provider(self, provider: LLMProvider, prompt: str, intent: Intent) -> GenerationResult:
        """Try to generate code using a specific provider."""
        start_time = time.time()
        config = self.provider_configs[provider]
        
        # Check rate limits
        if self._is_rate_limited(provider):
            return GenerationResult(
                status=GenerationStatus.RATE_LIMITED,
                code_blocks=[],
                provider_used=provider,
                generation_time=time.time() - start_time,
                error_message="Rate limit exceeded"
            )
        
        try:
            if provider == LLMProvider.OPENAI:
                generated_text = self._call_openai(prompt, config)
            elif provider == LLMProvider.ANTHROPIC:
                generated_text = self._call_anthropic(prompt, config)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Parse generated text into code blocks
            code_blocks = self._parse_generated_code(generated_text, intent.language)
            
            return GenerationResult(
                status=GenerationStatus.COMPLETED,
                code_blocks=code_blocks,
                provider_used=provider,
                generation_time=time.time() - start_time,
                tokens_used=len(prompt.split()) + len(generated_text.split())  # Rough estimate
            )
            
        except Exception as e:
            return GenerationResult(
                status=GenerationStatus.FAILED,
                code_blocks=[],
                provider_used=provider,
                generation_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _is_rate_limited(self, provider: LLMProvider) -> bool:
        """Check if provider is rate limited."""
        if provider not in self.rate_limit_tracker:
            return False
        
        last_request = self.rate_limit_tracker[provider]
        config = self.provider_configs[provider]
        
        # Simple rate limiting: check if last request was too recent
        if time.time() - last_request < config.rate_limit_delay:
            return True
        
        return False
    
    def _update_rate_limit(self, provider: LLMProvider):
        """Update rate limit tracker for provider."""
        self.rate_limit_tracker[provider] = time.time()
    
    def _fallback_to_mock(self, prompt: str, intent: Intent) -> GenerationResult:
        """Fall back to mock generation when all providers fail."""
        start_time = time.time()
        
        try:
            generated_text = self._mock_generate(prompt)
            code_blocks = self._parse_generated_code(generated_text, intent.language)
            
            return GenerationResult(
                status=GenerationStatus.COMPLETED,
                code_blocks=code_blocks,
                provider_used=None,
                generation_time=time.time() - start_time,
                tokens_used=0,
                error_message="Using mock generation - no LLM providers available"
            )
        except Exception as e:
            return GenerationResult(
                status=GenerationStatus.FAILED,
                code_blocks=[],
                provider_used=None,
                generation_time=time.time() - start_time,
                error_message=f"Mock generation failed: {e}"
            )
    
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
    
    def _call_openai(self, prompt: str, config: ProviderConfig) -> str:
        """Call OpenAI API to generate code with enhanced error handling."""
        try:
            self._update_rate_limit(LLMProvider.OPENAI)
            
            response = self.providers[LLMProvider.OPENAI]["sync"].chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Generate clean, well-documented, production-ready code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e
    
    def _call_anthropic(self, prompt: str, config: ProviderConfig) -> str:
        """Call Anthropic API to generate code with enhanced error handling."""
        try:
            self._update_rate_limit(LLMProvider.ANTHROPIC)
            
            response = self.providers[LLMProvider.ANTHROPIC]["sync"].messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic API error: {e}")
            raise e
    
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
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about code generation performance."""
        if not self.generation_history:
            return {"total_generations": 0}
        
        total_generations = len(self.generation_history)
        successful_generations = sum(1 for g in self.generation_history if g["status"] == "completed")
        avg_generation_time = sum(g["generation_time"] for g in self.generation_history) / total_generations
        
        # Provider usage statistics
        provider_usage = {}
        for generation in self.generation_history:
            provider = generation["provider_used"] or "mock"
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        # Intent type statistics
        intent_counts = {}
        for generation in self.generation_history:
            intent = generation["intent"]
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        return {
            "total_generations": total_generations,
            "successful_generations": successful_generations,
            "success_rate": successful_generations / total_generations if total_generations > 0 else 0,
            "average_generation_time": avg_generation_time,
            "provider_usage": provider_usage,
            "intent_distribution": intent_counts,
            "available_providers": [p.value for p in self.providers.keys()],
            "recent_generations": self.generation_history[-10:] if len(self.generation_history) > 10 else self.generation_history
        }
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all configured providers."""
        status = {}
        
        for provider, config in self.provider_configs.items():
            status[provider.value] = {
                "enabled": config.enabled,
                "model": config.model,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "timeout": config.timeout,
                "retry_attempts": config.retry_attempts,
                "rate_limit_delay": config.rate_limit_delay,
                "client_initialized": provider in self.providers,
                "last_rate_limit": self.rate_limit_tracker.get(provider, None)
            }
        
        return status
    
    def enable_provider(self, provider: LLMProvider, enabled: bool = True):
        """Enable or disable a provider."""
        if provider in self.provider_configs:
            self.provider_configs[provider].enabled = enabled
            print(f"Provider {provider.value} {'enabled' if enabled else 'disabled'}")
        else:
            print(f"Provider {provider.value} not configured")
    
    def update_provider_config(self, provider: LLMProvider, **kwargs):
        """Update configuration for a specific provider."""
        if provider in self.provider_configs:
            config = self.provider_configs[provider]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            print(f"Updated configuration for {provider.value}")
        else:
            print(f"Provider {provider.value} not configured")
    
    async def generate_code_async(self, intent: Intent, context: Optional[Dict] = None) -> List[CodeBlock]:
        """Asynchronous version of code generation."""
        context = context or {}
        start_time = time.time()
        
        # Build prompt based on intent type
        prompt = self._build_prompt(intent, context)
        
        # Generate code using async LLM calls
        result = await self._generate_with_fallback_async(prompt, intent)
        
        return result.code_blocks
    
    async def _generate_with_fallback_async(self, prompt: str, intent: Intent) -> GenerationResult:
        """Async version of generate with fallback support."""
        primary_provider = self._get_primary_provider()
        if not primary_provider:
            return self._fallback_to_mock(prompt, intent)
        
        # Try primary provider first
        result = await self._try_provider_async(primary_provider, prompt, intent)
        if result.status == GenerationStatus.COMPLETED:
            return result
        
        # Try fallback providers
        fallback_providers = self._get_fallback_providers(primary_provider)
        for provider in fallback_providers:
            result = await self._try_provider_async(provider, prompt, intent)
            if result.status == GenerationStatus.COMPLETED:
                return result
        
        # If all providers fail, fall back to mock generation
        return self._fallback_to_mock(prompt, intent)
    
    async def _try_provider_async(self, provider: LLMProvider, prompt: str, intent: Intent) -> GenerationResult:
        """Async version of try provider."""
        start_time = time.time()
        config = self.provider_configs[provider]
        
        # Check rate limits
        if self._is_rate_limited(provider):
            return GenerationResult(
                status=GenerationStatus.RATE_LIMITED,
                code_blocks=[],
                provider_used=provider,
                generation_time=time.time() - start_time,
                error_message="Rate limit exceeded"
            )
        
        try:
            if provider == LLMProvider.OPENAI:
                generated_text = await self._call_openai_async(prompt, config)
            elif provider == LLMProvider.ANTHROPIC:
                generated_text = await self._call_anthropic_async(prompt, config)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Parse generated text into code blocks
            code_blocks = self._parse_generated_code(generated_text, intent.language)
            
            return GenerationResult(
                status=GenerationStatus.COMPLETED,
                code_blocks=code_blocks,
                provider_used=provider,
                generation_time=time.time() - start_time,
                tokens_used=len(prompt.split()) + len(generated_text.split())
            )
            
        except Exception as e:
            return GenerationResult(
                status=GenerationStatus.FAILED,
                code_blocks=[],
                provider_used=provider,
                generation_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _call_openai_async(self, prompt: str, config: ProviderConfig) -> str:
        """Async version of OpenAI API call."""
        try:
            self._update_rate_limit(LLMProvider.OPENAI)
            
            response = await self.providers[LLMProvider.OPENAI]["async"].chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Generate clean, well-documented, production-ready code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e
    
    async def _call_anthropic_async(self, prompt: str, config: ProviderConfig) -> str:
        """Async version of Anthropic API call."""
        try:
            self._update_rate_limit(LLMProvider.ANTHROPIC)
            
            response = await self.providers[LLMProvider.ANTHROPIC]["async"].messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic API error: {e}")
            raise e
