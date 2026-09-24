from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True)

def test_validator():
    r=run('-m','tools.zdf','validate')
    assert r.returncode==0, r.stdout+r.stderr

def test_stats():
    r=run('-m','tools.zdf','stats')
    assert r.returncode==0
