from src.core.code_generator import CodeGenerator
from src.core.prompt_manager import PromptTemplateManager
from src.core.models import Intent, AgentConfig

# 1. Config
config = AgentConfig(
    openai_api_key="DUMMY_KEY",
    anthropic_api_key="DUMMY_KEY",
    model="text-davinci-003",
    llm_provider="openai"  # primary provider
)

# 2. Prompt manager
prompt_manager = PromptTemplateManager(prompt_dir="src/prompts")

# 3. Code generator
codegen = CodeGenerator(config, prompt_manager)

# 4. Test intent
intent = Intent(
    type="create_function",
    parameters={"description": "adds two numbers"}
)

# 5. Context (empty)
context = {}

# 6. Generate prompt (for debugging)
prompt_text = codegen._build_prompt(intent, context)
print("=== Generated Prompt ===")
print(prompt_text)

# 7. Simulate code generation (mock)
def mock_generate_code(intent, context):
    return """def add_numbers(a: float, b: float) -> float:
    \"\"\"Adds two numbers and returns the result.

    Parameters:
        a (float): First number.
        b (float): Second number.

    Returns:
        float: Sum of a and b.
    \"\"\"
    return a + b
"""

# 8. Use mock instead of real API call
generated_code = mock_generate_code(intent, context)

print("=== Generated Python Code ===")
print(generated_code)
