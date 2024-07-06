import json
import os
import re
from typing import Dict, Any, Optional

from consts import VALUE_TYPES, SCORE_PATTERN, COUNT_PATTERN


def build_dir_tree(start_dir: str) -> Dict[str, Any]:
    """
    Builds a nested dictionary representing the folder structure starting from the given path.

    Args:
        start_dir (str): The root directory from which to start building the folder structure.

    Returns:
        Dict[str, Any]: A nested dictionary representing the folder structure.
    """
    tree = {}
    for root, dirs, files in os.walk(start_dir):
        # Calculate the relative path and depth level
        relative_path = os.path.relpath(root, start_dir)
        parts = relative_path.split(os.sep)

        # Navigate to the correct position in the tree dictionary
        sub_tree = tree
        for part in parts:
            if part == ".":
                continue
            sub_tree = sub_tree.setdefault(part, {})

        # Add files to the current directory level
        for file in files:
            sub_tree[file] = None

    return tree


def print_dir_tree(tree: Dict[str, Any], prefix: str = "") -> None:
    """
    Prints a nested dictionary representing the folder structure in a tree-like format,
    including "..." under hidden directories instead of their contents.

    Args:
        tree (Dict[str, Any]): The nested dictionary representing the folder structure.
        prefix (str): The current prefix used for indentation (used for recursive calls).
    """
    entries = list(tree.keys())
    entries.sort(key=lambda e: (e.startswith("."), e))  # Sort entries with hidden files last
    for i, key in enumerate(entries):
        connector = "├── " if i < len(entries) - 1 else "└── "
        print(f"{prefix}{connector}{key}")
        extension = "│   " if i < len(entries) - 1 else "    "
        if isinstance(tree[key], dict):
            if key.startswith("."):  # Check if the directory is hidden
                print(f"{prefix+extension}└──    ...")  # Print "..." to indicate hidden content
                continue  # Skip the recursive call to avoid printing the hidden directory's contents
            else:

                print_dir_tree(tree[key], prefix + extension)


def fix_json_string(s: str) -> Any:
    """
    Attempts to fix common issues in a JSON string and parse it into a Python object.

    This function looks for unescaped quotes causing JSON parsing errors and escapes them
    correctly to produce a valid JSON string.

    Args:
        s (str): The JSON string to fix and parse.

    Returns:
        Any: The parsed JSON object.

    Raises:
        ValueError: If the JSON string cannot be parsed after attempts to fix it.
    """
    while True:
        try:
            # Try to parse the JSON string
            result = json.loads(s)
            # Parsing succeeded, exit the loop
            break
        except Exception as e:
            # Extract the position of the unexpected character from the exception message
            match = re.search(r"\(char (\d+)\)", str(e))
            if not match:
                raise ValueError("JSON parsing error cannot be resolved.")

            # Position of the unexpected character
            unexp = int(match.group(1))

            # Position of the unescaped double quote before the unexpected character
            unesc = s.rfind(r'"', 0, unexp)

            # Escape the unescaped double quote
            s = s[:unesc] + r"\"" + s[unesc + 1 :]

            # Position of the corresponding closing double quote (+2 for inserted '\')
            closg = s.find(r'"', unesc + 2)

            # Escape the closing double quote
            s = s[:closg] + r"\"" + s[closg + 1 :]

    return result


def convert_score(score_str: str) -> float:
    """Converts a score string to a float."""
    try:
        return float(score_str.split("/")[0])  # Example: "4.5 / 5" -> 4.5
    except ValueError:
        raise ValueError(f"Invalid score string: {score_str}")


def convert_count(count_str: str) -> int:
    """Converts a count string to an integer."""
    try:
        return int(count_str.replace(",", ""))  # Example: "1,234" -> 1234
    except ValueError:
        raise ValueError(f"Invalid count string: {count_str}")


def normalize_vals(value: Optional[str]) -> VALUE_TYPES:
    """
    Normalizes a value extracted from the RoyalRoad website.

    If the value matches the format of a score or a count, it is converted to a float or an integer, respectively.
    Otherwise, the original value is returned.

    Args:
        value: The value to normalize.

    Returns:
        The normalized value.

    Raises:
        ValueError: If the value is a score or a count string but cannot be converted to a float or an integer.
    """
    if value is None:
        return value
    if isinstance(value, (int, float)):
        return value

    value = value.strip()

    if SCORE_PATTERN.match(value):
        return convert_score(value)

    if COUNT_PATTERN.match(value):
        return convert_count(value)

    return value.replace("\xa0", " ")


if __name__ == "__main__":
    # use the project directory
    # start_dir = os.path.dirname(os.path.abspath(__file__))
    start_dir = r"C:\Users\yoav\PycharmProjects\rrscrape"
    folder_structure = build_dir_tree(start_dir)
    print_dir_tree(folder_structure)
