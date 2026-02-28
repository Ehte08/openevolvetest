"""
OpenEvolve will modify ONLY the code inside the EVOLVE block.
Keep the public interface stable: sort_fn(arr) -> sorted list.
"""

from typing import List

def sort_fn(arr: List[int]) -> List[int]:
    # Make a copy so we don't mutate input (helps evaluation fairness)
    a = list(arr)

    # EVOLVE-BLOCK-START
    # Highly optimized: Python's built-in Timsort (O(n log n) time complexity)
    a.sort()
    # EVOLVE-BLOCK-END

    return a