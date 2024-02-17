def longest_common_prefix(strings: list[str]) -> str:
    if not strings:
        return ""
    shortest_str: str = str(min(strings, key=len))
    for i, char in enumerate(shortest_str):
        for other in strings:
            if other[i] != char:
                return shortest_str[:i]
    return shortest_str
