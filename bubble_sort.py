def bubble_sort(arr):
    """
    Sort an array using the bubble sort algorithm.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        List: Sorted array
        
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


# Example usage
if __name__ == "__main__":
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original: {test_array}")
    sorted_array = bubble_sort(test_array.copy())
    print(f"Sorted: {sorted_array}")