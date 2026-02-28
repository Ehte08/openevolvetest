"""
OpenEvolve will modify ONLY the code inside the EVOLVE block.
Keep the public interface stable: sort_fn(arr) -> sorted list.
"""

from typing import List

def sort_fn(arr: List[int]) -> List[int]:
    # Make a copy so we don't mutate input (helps evaluation fairness)
    a = list(arr)

    # EVOLVE-BLOCK-START
    # Baseline: bubble sort
    n = len(a)
    for i in range(n):
        for j in range(0, n - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    # EVOLVE-BLOCK-END

    return a