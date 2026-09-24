from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def test_case_files_exist():
    index=yaml.safe_load((ROOT/'corpus/cases.yaml').read_text())
    ids={x['case_id'] for x in index}
    files={p.stem for p in (ROOT/'cases').glob('*.yaml')}
    assert ids == files

def test_no_real_exploit_instructions():
    banned=('PRIVATE_KEY=', 'mnemonic=', 'cast send', 'anvil --fork', 'flashbots')
    for p in (ROOT/'cases').glob('*.yaml'):
        text=p.read_text().lower()
        for x in banned:
            assert x.lower() not in text, f'banned operational content in {p}'
