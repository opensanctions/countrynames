import os
import yaml
import logging
from typing import List, Dict, Set, Tuple
from collections import defaultdict

from countrynames.util import process_data

log = logging.getLogger("countrynames.compile")
CODE_DIR = os.path.dirname(__file__)


def load_yaml_data() -> Dict[str, List[str]]:
    data = defaultdict(list)
    data_file = os.path.join(CODE_DIR, "data.yaml")
    with open(data_file, "r", encoding="utf-8") as fh:
        for code, names in yaml.safe_load(fh).items():
            data[code].extend(names)
    return data


def write_python(data: Dict[str, List[str]]) -> None:
    python_file = os.path.join(CODE_DIR, "data.py")
    with open(python_file, "w", encoding="utf-8") as pyfh:
        pyfh.write("# generated file, do not edit.\n")
        pyfh.write("from typing import Dict, List\n\n")
        pyfh.write("DATA: Dict[str, List[str]] = {}\n")
        for code, names in data.items():
            code = code.strip().upper()
            pyfh.write("DATA[%r] = %r\n" % (code, names))


def validate_data(data: Dict[str, List[str]]) -> None:
    """Run a check on the country name database."""
    mappings: Dict[str, Set[Tuple[str, str]]] = {}
    for code, norm, original in process_data(data):
        mappings.setdefault(norm, set())
        mappings[norm].add((code, original))
    for norm, assigned in mappings.items():
        countries = set([c for (c, _) in assigned])
        if len(countries) == 1:
            continue
        log.warning("Ambiguous string [%s]: %r", norm, assigned)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        # Explicitly test the import as it could be broken after OS upgrades. In that case
        # a broken data.py will be generated, because normality has a fallback.
        from icu import Transliterator  # type: ignore
    except ImportError as e:
        log.error("Loading PyICU failed: %r. Normalized names will be broken, refusing to compile.", e)
        exit(1)
    data = load_yaml_data()
    validate_data(data)
    write_python(data)
