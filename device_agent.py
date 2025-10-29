import argparse
import json
import sys
import os

# Assuming tool wrappers are available in a 'core/tools' directory relative to this script
# On the Android device, the project would be cloned, so paths would be relative.
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'tools'))

from tools.nuclei_wrapper import NucleiWrapper
# from tools.subfinder_wrapper import SubfinderWrapper # Add as needed

def main():
    parser = argparse.ArgumentParser(description='Wilsons-Raiders Device Agent for Termux')
    parser.add_argument('--scan', choices=['nuclei', 'subfinder'], help='Type of scan to perform.')
    parser.add_argument('--target', required=True, help='The target for the scan.')
    
    args = parser.parse_args()

    results = {}
    if args.scan == 'nuclei':
        nuclei_scanner = NucleiWrapper(args.target)
        scan_output = nuclei_scanner.run()
        results = {"tool": "nuclei", "target": args.target, "output": scan_output}
    elif args.scan == 'subfinder':
        # Placeholder for subfinder
        # subfinder_scanner = SubfinderWrapper(args.target)
        # scan_output = subfinder_scanner.run()
        # results = {"tool": "subfinder", "target": args.target, "output": scan_output}
        results = {"tool": "subfinder", "target": args.target, "output": "Subfinder not yet implemented on device agent."}
    else:
        results = {"error": "Invalid scan type specified."}

    print(json.dumps(results))

if __name__ == "__main__":
    main()
