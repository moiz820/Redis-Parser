# parsers/slowlog_parser.py

import subprocess

def parse_slowlog(nodes):
    for node in nodes:
        host = node['host']
        port = node['port']
        name = node['name']

        print(f"[+] Fetching SLOWLOG from {name} at {host}:{port}")
        try:
            result = subprocess.run(
                ['redis-cli', '-h', host, '-p', str(port), 'SLOWLOG', 'GET'],
                capture_output=True, text=True, timeout=5
            )
            output_file = f"logs/{name}_slowlog.txt"
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            print(f"[✓] Output saved to {output_file}")
        except Exception as e:
            print(f"[!] Failed to fetch SLOWLOG from {name}: {e}")
