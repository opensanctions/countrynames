# countrynames

[![build](https://github.com/opensanctions/countrynames/actions/workflows/build.yml/badge.svg)](https://github.com/opensanctions/countrynames/actions/workflows/build.yml)

This library helps with the mapping of country names to their respective
two or three letter codes. The idea is
to incorporate common names for countries, and even some limited misspellings,
as they occur in source data.

There is also support for fuzzy matching, which uses a heuristic based on levenshtein distance.

## Usage

```python
import countrynames

assert 'DE' == countrynames.to_code('Germany')
assert 'DE' == countrynames.to_code('Bundesrepublik Deutschland')
assert 'DE' == countrynames.to_code('Bundesrepublik Deutschlan', fuzzy=True)
assert 'DE' == countrynames.to_code('DE')
assert 'DEU' == countrynames.to_code_3('Germany')
```

## Non-standard country codes

* ``XK`` or ``XKX`` - Kosovo
* ``EU`` or ``EUU`` - European Union

For some dissolved countries (e.g. `SUHH` for Soviet Union) and sub-regions
(e.g. `GB-SCT` for Scotland) special codes are defined and returned from both
`to_code` and `to_code_3`.

## How to release

```sh
make test compile
git commit countrynames/data.py -m "update data.py"
bump2version --verbose patch
git push --all
```
