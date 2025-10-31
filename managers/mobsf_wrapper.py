import subprocess, json

def run_mobsf(apk_path):
    # Assumes MobSF is running as a service and API key is set in env
    import os, requests
    mobsf_api = os.getenv('MOBSF_API_KEY')
    mobsf_url = os.getenv('MOBSF_URL', 'http://localhost:8000')
    headers = {'Authorization': mobsf_api}
    with open(apk_path, 'rb') as f:
        files = {'file': (apk_path, f)}
        r = requests.post(f'{mobsf_url}/api/v1/upload', files=files, headers=headers)
        scan = r.json()
    scan_hash = scan.get('hash')
    r = requests.post(f'{mobsf_url}/api/v1/report_json', data={'hash': scan_hash}, headers=headers)
    return r.json()
