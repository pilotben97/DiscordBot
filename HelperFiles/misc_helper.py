import re

def is_valid_hex(hex_code: str) -> bool:
    return bool(re.fullmatch(r"[0-9A-Fa-f]{6}", hex_code.strip()))