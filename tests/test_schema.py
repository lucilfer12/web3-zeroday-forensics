import json, yaml
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas/case.schema.json').read_text())
V=Draft202012Validator(SCHEMA, format_checker=FormatChecker())

def test_all_case_schema_records():
    for p in (ROOT/'cases').glob('*.yaml'):
        c=yaml.safe_load(p.read_text())
        errs=list(V.iter_errors(c))
        assert not errs, '\n'.join(e.message for e in errs)
