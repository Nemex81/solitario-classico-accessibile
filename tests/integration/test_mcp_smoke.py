import sys
import os
import json
import subprocess


def test_mcp_smoke_runs_client():
    script = os.path.join('scripts', 'test_mcp_client.py')
    assert os.path.exists(script), f"test harness missing: {script}"

    proc = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise AssertionError(f"mcp client failed (code={proc.returncode})\nstderr:\n{proc.stderr}\nstdout:\n{proc.stdout}")

    out = proc.stdout.strip()
    assert out, "no output from client"
    try:
        obj = json.loads(out)
    except Exception as e:
        raise AssertionError(f"output is not valid JSON: {e}\nstdout:\n{out}")

    assert 'response' in obj, f"unexpected client response shape: {obj}"
    # check we received a JSON-RPC style result or error
    resp = obj['response']
    assert isinstance(resp, dict), "response must be a JSON object"
    assert 'result' in resp or 'error' in resp, f"no result/error in response: {resp}"
