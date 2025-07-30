import subprocess
import json
import os

def run_lynis(target, extra_args=None):
    cmd = ['lynis', 'audit', 'system', '--report-file', 'lynis-report.json']
    if extra_args:
        cmd += extra_args
    env = os.environ.copy()
    results = []
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
        for line in proc.stdout:
            try:
                results.append(json.loads(line.strip()))
            except Exception:
                continue
        proc.wait()
    except Exception as e:
        results.append({'error': str(e)})
    return results
