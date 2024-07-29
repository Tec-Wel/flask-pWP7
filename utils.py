"""
Utility functions for the recommender system.
"""


def print_dict(count: int, dictionary: dict, preamble: str = "") -> None:
    """
    Print the first `count` key-value pairs in the dictionary.
    """
    print(preamble)
    count = 0
    for key, value in dictionary.items():
        print("Key:", key, "Value:", value)
        print()
        count += 1
        if count == 1:
            break

def print_list(arr: list, preamble: str = "") -> None:
    """
    Print the list of items.
    """
    print(preamble)
    if len(arr) == 0:
        print("[Empty List]")
    for i, item in enumerate(arr):
        print(f"{i+1}: {item}")
    print()