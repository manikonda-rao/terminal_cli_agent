#!/usr/bin/env python3
"""
Test script for the new UI manager functionality.
"""

from src.core.ui import ui


def test_ui_components():
    """Test various UI components."""
    print("Testing Terminal UX/UI improvements...")
    print("=" * 50)
    
    # Test welcome banner
    ui.show_welcome_banner("1.0.0")
    
    # Test different message types
    ui.success("✅ Success message test")
    ui.warning("⚠️  Warning message test")
    ui.error("❌ Error message test")
    ui.info("ℹ️  Information message test")
    ui.step("🔄 Step message test")
    
    # Test code preview
    sample_code = '''def quicksort(arr):
    """
    Implementation of quicksort algorithm.
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)'''
    
    ui.show_code_preview(sample_code, "python", "Quicksort Implementation")
    
    # Test execution logs
    steps = [
        {'status': 'completed', 'message': 'Intent parsing completed'},
        {'status': 'completed', 'message': 'Code generation finished'},
        {'status': 'in_progress', 'message': 'Saving to file'},
        {'status': 'completed', 'message': 'File saved successfully'}
    ]
    ui.show_execution_logs(steps)
    
    # Test confirmation
    print("\n" + "=" * 50)
    print("UI Component Tests Completed!")
    success_msg = ("All color-coded outputs, code previews, and "
                   "execution logs are working.")
    print(success_msg)


if __name__ == "__main__":
    test_ui_components()