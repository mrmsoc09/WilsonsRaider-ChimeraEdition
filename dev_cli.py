#!/usr/bin/env python3
import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Wilsons-Raiders Dev CLI')
    parser.add_argument('action', choices=['setup', 'build', 'run', 'lint', 'test', 'clean'], help='Action to perform')
    args = parser.parse_args()
    cmds = {
        'setup': 'pip install -r requirements.txt',
        'build': 'docker-compose build',
        'run': 'docker-compose up',
        'lint': 'flake8 orchestrator.py secret_manager.py hackerone_reporter.py tool_wrappers/ ai_agents/',
        'test': 'pytest',
        'clean': 'docker-compose down -v && rm -rf __pycache__ .pytest_cache',
    }
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(cmds[args.action], shell=True)

if __name__ == '__main__':
    main()
