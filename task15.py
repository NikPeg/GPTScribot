import re


def remove_comments(java_code: str) -> str:
    pattern: str = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//.*?$)"
    regex: re.Pattern = re.compile(pattern, re.DOTALL | re.MULTILINE)

    def replacer(match: re.Match) -> str:
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)

    return regex.sub(replacer, java_code)
