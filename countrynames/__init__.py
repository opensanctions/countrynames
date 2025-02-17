import logging
from functools import lru_cache
from typing import Any, Optional, Dict, Set

from countrynames.mappings import mappings
from countrynames.util import normalize_name, process_data
from rapidfuzz.distance import Levenshtein

log = logging.getLogger(__name__)

__all__ = ["to_code", "to_code_3", "validate_data"]

LOWERCASE_COUNTRY_NAME_TO_CODE: Dict[str, str] = {}
NORMALIZED_COUNTRY_NAME_TO_CODE: Dict[str, str] = {}
ALL_COUNTRY_CODES: Set[str] = set()


def _load_data() -> None:
    """Load known aliases from a YAML file. Internal."""
    from countrynames.data import DATA

    normalized_name_to_code = dict()
    lower_name_to_code = dict()
    for code, normalized_name, name in process_data(DATA):
        lower_name_to_code[name.lower()] = code
        normalized_name_to_code[normalized_name] = code

    LOWERCASE_COUNTRY_NAME_TO_CODE.update(lower_name_to_code)
    NORMALIZED_COUNTRY_NAME_TO_CODE.update(normalized_name_to_code)
    ALL_COUNTRY_CODES.update(NORMALIZED_COUNTRY_NAME_TO_CODE.values())


def _fuzzy_search(name: str) -> Optional[str]:
    best_code = None
    best_distance = None
    for cand, code in NORMALIZED_COUNTRY_NAME_TO_CODE.items():
        if len(cand) <= 4:
            continue
        distance = Levenshtein.distance(name, cand)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_code = code
    if best_distance is None or best_distance > (len(name) * 0.15):
        return None
    log.debug(
        "Guessing country: %s -> %s (distance %d)", name, best_code, best_distance
    )
    return best_code


@lru_cache(maxsize=None)
def to_code(
    country_name: Any, fuzzy: bool = False, default: Optional[str] = None
) -> Optional[str]:
    """Given a human name for a country, return a two letter code.

    Arguments:
        ``fuzzy``: Try fuzzy matching based on Levenshtein distance.
    """
    # Lazy load country list
    if not len(NORMALIZED_COUNTRY_NAME_TO_CODE) or not len(LOWERCASE_COUNTRY_NAME_TO_CODE):
        _load_data()

    country_name = country_name.strip()

    # shortcut before costly ICU stuff if input is actually an ISO code
    if isinstance(country_name, str):
        if country_name.upper() in ALL_COUNTRY_CODES:
            return country_name

    # Try to find an exact match
    # code = LOWERCASE_COUNTRY_NAME_TO_CODE.get(country_name.lower())
    # if code == "FAIL":
    #     return default
    # if code is not None:
    #     return code

    # Transliterate and clean up, this removes accents and other noise but can be too reductionist on non-latin scripts.
    # But we've already done an exact match lookup above.
    normalized_name = normalize_name(country_name)
    if normalized_name is None:
        return default
    code = NORMALIZED_COUNTRY_NAME_TO_CODE.get(normalized_name)
    if code == "FAIL":
        return default

    # Find closest match with spelling mistakes
    if code is None and fuzzy is True:
        code = _fuzzy_search(normalized_name)
    return code or default


def to_code_3(country_name: Any, fuzzy: bool = False) -> Optional[str]:
    """Given a human name for a country, return a three letter code.

    Arguments:
        ``fuzzy``: Try fuzzy matching based on levenshtein distance.
    """
    code = to_code(country_name, fuzzy=fuzzy)
    if code and len(code) > 2:
        return code
    elif code is None:
        return code
    else:
        return mappings[code]
