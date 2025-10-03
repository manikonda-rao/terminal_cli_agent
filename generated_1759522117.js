def quicksort(arr):
    """
    Sort an array using the quicksort algorithm.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        List: Sorted array
        
    Time Complexity: O(n log n) average case, O(n²) worst case
    Space Complexity: O(log n) average case
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


# Example usage
if __name__ == "__main__":
    test_array = [3, 6, 8, 10, 1, 2, 1]
    print(f"Original: {test_array}")
    sorted_array = quicksort(test_array)
    print(f"Sorted: {sorted_array}")