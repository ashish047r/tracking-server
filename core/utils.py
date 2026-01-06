from urllib.parse import urlencode, urlparse


def build_final_suffix(param_map: dict) -> str:
    """
    Deterministic & Google-safe
    """
    return urlencode(param_map)


def extract_full_query(final_url: str) -> str:
    """
    Returns everything after ? without decoding
    """
    parsed = urlparse(final_url)
    return parsed.query or ""
