#!/usr/bin/env python3
"""
Semplice client di smoke test per lo scf-mcp server via stdio JSON-RPC.

Avvia `scf-mcp/scf-mcp-server.py` come subprocess, invia una richiesta
`scf_get_workspace_info` e stampa la risposta JSON ricevuta.

Uso previsto (da shell):
  python scripts/test_mcp_client.py
"""
import sys
import os
import json
import time
import queue
import threading
from subprocess import Popen, PIPE


def reader_thread(stream, q):
    try:
        for line in iter(stream.readline, ''):
            if not line:
                break
            q.put(line)
    finally:
        try:
            stream.close()
        except Exception:
            pass


def main():
    project_root = os.getcwd()
    server_path = os.path.join(project_root, 'scf-mcp', 'scf-mcp-server.py')
    if not os.path.exists(server_path):
        print(json.dumps({"error": "server script not found", "path": server_path}))
        sys.exit(2)

    env = os.environ.copy()
    env['WORKSPACE_FOLDER'] = project_root

    p = Popen([sys.executable, server_path], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, env=env)

    q = queue.Queue()
    t = threading.Thread(target=reader_thread, args=(p.stdout, q), daemon=True)
    t.start()

    # Costruisci richiesta JSON-RPC
    req = {"jsonrpc": "2.0", "id": 1, "method": "scf_get_workspace_info", "params": {}}
    try:
        p.stdin.write(json.dumps(req) + "\n")
        p.stdin.flush()
    except Exception as e:
        print(json.dumps({"error": "write failed", "exc": str(e)}))
        p.terminate()
        sys.exit(3)

    deadline = time.time() + 12.0
    parsed = None
    while time.time() < deadline:
        try:
            line = q.get(timeout=0.5)
        except queue.Empty:
            if p.poll() is not None:
                break
            continue
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        parsed = obj
        break

    try:
        p.terminate()
    except Exception:
        pass
    try:
        p.wait(timeout=5)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass

    if parsed is None:
        print(json.dumps({"error": "no-json-response"}))
        sys.exit(4)

    print(json.dumps({"response": parsed}))
    sys.exit(0)


if __name__ == '__main__':
    main()
