import re
import json
import ast
from typing import Any, Union

from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="agent.log")

def clean_json_string(raw: str) -> str:
    """
    Cleans noisy JSON-like text with emojis, escape issues, and invalid structures.
    Returns a normalized JSON string.
    """
    if not raw:
        return ""

    # Remove Markdown and code fences
    cleaned = raw.strip().replace("```json", "").replace("```", "")

    # Remove control chars except standard whitespace and emoji
    cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", cleaned)

    # Extract JSON boundaries
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1 or start >= end:
        logger.warning("[clean_json_string] No valid JSON boundaries found.")
        return ""

    json_content = cleaned[start:end + 1]

    # Replace Pythonic values
    json_content = re.sub(r"\bNone\b", "null", json_content)
    json_content = re.sub(r"\bTrue\b", "true", json_content)
    json_content = re.sub(r"\bFalse\b", "false", json_content)

    # Escape invalid backslashes
    json_content = re.sub(r'(?<!\\)\\(?![ntr"\\/bfu])', r'\\\\', json_content)

    # Normalize quotes
    json_content = re.sub(r"(?<!\\)'", '"', json_content)

    # Fix trailing commas
    json_content = re.sub(r",\s*([}\]])", r"\1", json_content)

    # Clean up extra spaces
    json_content = re.sub(r"\s+", " ", json_content)

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
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"[safe_json_loads] Standard JSON decode failed: {e}")

    # Attempt 2: Decode emojis safely
    try:
        return json.loads(cleaned.encode("utf-8", "ignore").decode("utf-8"))
    except Exception as e:
        logger.warning(f"[safe_json_loads] UTF-8 emoji decode failed: {e}")

    # Attempt 3: literal_eval fallback for Pythonic dicts
    try:
        return ast.literal_eval(cleaned)
    except Exception as e:
        logger.warning(f"[safe_json_loads] literal_eval failed: {e}")

    # Attempt 4: JSON5-style repair (fix unquoted keys)
    try:
        fixed = re.sub(r"(['\"])?([A-Za-z0-9_]+)\1?\s*:", r'"\2":', cleaned)
        fixed = re.sub(r"'", '"', fixed)
        return json.loads(fixed)
    except Exception as e:
        logger.warning(f"[safe_json_loads] Fallback failed: {e}")

    # If all fails, log and return empty dict
    snippet = cleaned[:200].replace("\n", " ")
    logger.error(f"[safe_json_loads] All decoding attempts failed. Snippet: {snippet}...")
    return {}
