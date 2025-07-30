import subprocess
import json
import os
from typing import List, Dict, Any

def run_nuclei(target: str, templates: str = None, proxychains_path: str = '/usr/bin/proxychains4', nuclei_path: str = '/usr/local/bin/nuclei', extra_args: List[str] = None) -> List[Dict[str, Any]]:
    cmd = [proxychains_path, nuclei_path, '-u', target, '-json']
    if templates:
        cmd += ['-t', templates]
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
