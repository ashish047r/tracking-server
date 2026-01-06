from urllib.parse import urlencode


def build_final_suffix(param_map: dict) -> str:
    """
    Deterministic & Google-safe
    """
    return urlencode(param_map)
