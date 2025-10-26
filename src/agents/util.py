import re
import json
import ast
from typing import Any, Union

from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="agent.log")

def clean_json_string(raw: str) -> str:
    """
    Cleans JSON-like text without breaking UTF-8 or emojis.
    Removes markdown fences, control characters, and fixes quotes safely.
    """
    if not raw:
        return ""

    # Remove Markdown/code fences robustly
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    # Extract JSON between first '{' and last '}'
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1 or start >= end:
        logger.warning("[clean_json_string] No valid JSON boundaries found.")
        return ""

    json_content = cleaned[start:end + 1]

    # Convert Pythonic values
    json_content = re.sub(r"\bNone\b", "null", json_content)
    json_content = re.sub(r"\bTrue\b", "true", json_content)
    json_content = re.sub(r"\bFalse\b", "false", json_content)

    # Escape invalid backslashes (but preserve valid escape sequences)
    json_content = re.sub(r'\\(?![ntr"\\/bfu])', r'\\\\', json_content)

    # Remove trailing commas before } or ]
    json_content = re.sub(r",\s*([}\]])", r"\1", json_content)

    # Remove only ASCII control chars, not Unicode/emoji
    json_content = ''.join(ch for ch in json_content if ch >= ' ' or ch in '\n\r\t')

    return json_content.strip()


def safe_json_loads(raw: str) -> Union[dict, list]:
    """
    Safely loads malformed JSON, handling emojis, stray escapes, and Pythonic dicts.
    Returns an empty dict on total failure.
    """
    if not raw:
        return {}

    cleaned = clean_json_string(raw)

    # Attempt 1: Standard JSON
    try:
        logger.debug(f"[safe_json_loads] Cleaned JSON: {cleaned[:200]}")
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"[safe_json_loads] Standard JSON decode failed: {e}")

    # Attempt 2: Try with relaxed Unicode handling
    try:
        # Ensure proper UTF-8 encoding
        if isinstance(cleaned, str):
            cleaned_bytes = cleaned.encode('utf-8', errors='surrogatepass')
            cleaned = cleaned_bytes.decode('utf-8', errors='ignore')
        return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"[safe_json_loads] UTF-8 decode failed: {e}")

    # Attempt 3: Fix single quotes that are used as string delimiters (not apostrophes)
    # Only replace single quotes at key boundaries and string boundaries
    try:
        # Replace single quotes used as delimiters around keys
        fixed = re.sub(r"'(\w+)'(\s*):", r'"\1"\2:', cleaned)
        # Replace single quotes around string values (but this is tricky with apostrophes)
        # Safer to just try as-is first
        return json.loads(fixed)
    except Exception as e:
        logger.warning(f"[safe_json_loads] Quote fix failed: {e}")

    # Attempt 4: literal_eval fallback for Pythonic dicts
    try:
        return ast.literal_eval(cleaned)
    except Exception as e:
        logger.warning(f"[safe_json_loads] literal_eval failed: {e}")

    # If all fails, log and return empty dict
    snippet = cleaned[:200].replace("\n", " ")
    logger.error(f"[safe_json_loads] All decoding attempts failed. Snippet: {snippet}...")
    return {}