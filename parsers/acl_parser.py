# parsers/acl_parser.py
import subprocess
import os

def collect_acl_events(nodes):
    log_dir = "logs/acl"
    os.makedirs(log_dir, exist_ok=True)

    for node in nodes:
        host, port = node["host"], str(node["port"])
        node_name = node["name"]
        outfile_path = os.path.join(log_dir, f"{node_name}_acl.log")

        print(f"[+] Fetching ACL LOG entries for {node_name} at {host}:{port}")

        try:
            result = subprocess.run(
                ["redis-cli", "-h", host, "-p", port, "ACL", "LOG", "100"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"[!] redis-cli error: {result.stderr}")
                continue

            if result.stdout.strip():
                with open(outfile_path, "w") as f:
                    f.write(result.stdout)
                print(f"[+] ACL log saved to: {outfile_path}")
            else:
                print(f"[!] No ACL logs found for {node_name}.")

        except Exception as e:
            print(f"[!] Error fetching ACL LOG from {node_name}: {e}")

