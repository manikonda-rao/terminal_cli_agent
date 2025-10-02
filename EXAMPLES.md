# Terminal Coding Agent - Usage Examples

This document provides comprehensive examples of how to use the Terminal Coding Agent.
## Quick Start

1. **Install dependencies:**
 ```bash
 pip install -r requirements.txt
 ```

2. **Set up environment:**
 ```bash
 cp env.example .env
 # Edit .env with your API keys
 ```

3. **Run the CLI:**
 ```bash
 python -m src.cli.main
 ```
## Example Usage Scenarios
### 1. Creating Functions

```
> Create a Python function for quicksort
 Intent: create_function (confidence: 1.00)
 Generated 1 code block(s)
💾 Saved code to quicksort.py

 Generated Code:
def quicksort(arr):
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
 
 return quicksort(left) + middle + quicksort(right)
```
### 2. Modifying Code

```
> Modify the last function to handle empty lists
 Intent: modify_code (confidence: 1.00)
 Generated 1 code block(s)
💾 Saved code to quicksort.py

 Generated Code:
def quicksort(arr):
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
 
 return quicksort(left) + middle + quicksort(right)
```
### 3. Running Code

```
> Run the last function with [3, 1, 4, 1, 5, 9, 2, 6]
 Intent: run_code (confidence: 1.00)
 Generated 1 code block(s)
 Execution: completed

 Generated Code:
# Test the quicksort function
test_data = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"Original: {test_data}")
sorted_data = quicksort(test_data)
print(f"Sorted: {sorted_data}")

# Test with empty list
empty_list = []
print(f"Empty list: {quicksort(empty_list)}")

# Test with single element
single = [42]
print(f"Single element: {quicksort(single)}")

 Execution Results:
Status: completed
Execution Time: 0.123s

Output:
Original: [3, 1, 4, 1, 5, 9, 2, 6]
Sorted: [1, 1, 2, 3, 4, 5, 6, 9]
Empty list: []
Single element: [42]
```
### 4. Creating Classes

```
> Write a class for binary tree node
 Intent: create_class (confidence: 1.00)
 Generated 1 code block(s)
💾 Saved code to binary_tree_node.py

 Generated Code:
class BinaryTreeNode:
 """
 A node in a binary tree data structure.
 """
 
 def __init__(self, value):
 """
 Initialize a binary tree node.
 
 Args:
 value: The value stored in this node
 """
 self.value = value
 self.left = None
 self.right = None
 
 def insert(self, value):
 """
 Insert a value into the tree.
 
 Args:
 value: The value to insert
 """
 if value < self.value:
 if self.left is None:
 self.left = BinaryTreeNode(value)
 else:
 self.left.insert(value)
 else:
 if self.right is None:
 self.right = BinaryTreeNode(value)
 else:
 self.right.insert(value)
 
 def search(self, value):
 """
 Search for a value in the tree.
 
 Args:
 value: The value to search for
 
 Returns:
 True if value is found, False otherwise
 """
 if value == self.value:
 return True
 elif value < self.value and self.left:
 return self.left.search(value)
 elif value > self.value and self.right:
 return self.right.search(value)
 return False
```
### 5. Searching Code

```
> Search for "def quicksort"
 Intent: search_code (confidence: 1.00)
🔍 Search results for 'def quicksort':

 quicksort.py:
 1: def quicksort(arr):
 2: """
 3: Sort an array using the quicksort algorithm.
 4: Handles empty lists and single elements.
```
### 6. File Management

```
> Create a file called utils.py
 Intent: create_file (confidence: 1.00)
📄 Created file: utils.py

> Delete the file test.py
 Intent: delete_file (confidence: 1.00)
🗑️ Deleted file: test.py
```
### 7. Special Commands

```
> /status
📊 Project Status:
┌─────────────────┬─────────────────────────────┐
│ Metric │ Value │
├─────────────────┼─────────────────────────────┤
│ Project Root │ /path/to/project │
│ Active Files │ 3 │
│ Total Turns │ 7 │
│ Successful Turns│ 6 │
│ Failed Turns │ 1 │
│ Success Rate │ 85.7% │
└─────────────────┴─────────────────────────────┘

 Active Files:
 • quicksort.py
 • binary_tree_node.py
 • utils.py

 Intent Statistics:
 • create_function: 2
 • create_class: 1
 • modify_code: 1
 • run_code: 1
 • create_file: 1
 • delete_file: 1

> /rollback
↩️ Rolled back utils.py
 Rollback completed successfully
```
## Advanced Features
### Multi-turn Conversations

The agent maintains conversation context across interactions:

```
> Create a function to calculate fibonacci numbers
[Creates fibonacci.py]

> Modify it to use memoization
[Modifies fibonacci.py with memoization]

> Run it with n=10
[Executes fibonacci(10) and shows result]

> Explain how memoization works in this function
[Generates explanation of the memoization technique]
```
### Project State Persistence

The agent automatically:
- Saves conversation history
- Tracks active files
- Maintains project context
- Creates backups before modifications
- Enables rollback functionality
### Safe Execution

Code execution is sandboxed with:
- Resource limits (memory, CPU time)
- Process isolation
- Automatic cleanup
- Error handling and reporting
## Configuration Options

Create a custom configuration:

```python
from src.core.models import AgentConfig

config = AgentConfig(
 llm_provider="anthropic",
 model_name="claude-3-sonnet",
 temperature=0.2,
 max_execution_time=60,
 max_memory_mb=1024,
 enable_syntax_highlighting=True
)
```
## API Integration

The agent supports multiple LLM providers:

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3-sonnet, Claude-3-haiku
- **Mock Mode**: For testing without API keys
## Error Handling

The agent gracefully handles:
- Invalid natural language input
- Code generation failures
- Execution errors
- File system issues
- Network connectivity problems
## Best Practices

1. **Be specific**: "Create a function for binary search" vs "create a function"
2. **Use context**: Reference "the last function" for modifications
3. **Test frequently**: Use "run the last function" to test your code
4. **Use rollback**: If something goes wrong, use `/rollback`
5. **Check status**: Use `/status` to monitor your project
## Troubleshooting
### Common Issues

1. **"No module named 'openai'"**
 - Install dependencies: `pip install -r requirements.txt`

2. **"API key not found"**
 - Set up your API keys in the `.env` file

3. **"Execution failed"**
 - Check the generated code for syntax errors
 - Use `/rollback` to revert changes

4. **"Intent not recognized"**
 - Try rephrasing your request
 - Use more specific language
### Getting Help

- Use `/help` for command reference
- Use `/status` for project information
- Check the logs for detailed error messages
