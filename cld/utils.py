import re

def standardize_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z]', '', name)
