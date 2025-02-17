from normality import normalize
from typing import List, Iterator, Optional, Dict, Tuple


def normalize_name(country: Optional[str]) -> Optional[str]:
    """Clean up a country name before comparison."""
    return normalize(country, latinize=True)


def process_data(data: Dict[str, List[str]]) -> Iterator[Tuple[str, str, str]]:
    """For each mapped country name, return a tuple of code, normalized country name, country name.

    Internal use only."""

    for code, names in data.items():
        code = code.strip().upper()
        norm_code = normalize_name(code)
        if norm_code is not None:
            yield code, norm_code, code
        for name in names:
            norm_name = normalize_name(name)
            if norm_name is not None and norm_name is not "":
                yield code, norm_name, name
