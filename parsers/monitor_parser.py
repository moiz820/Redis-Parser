# parsers/monitor_parser.py
import subprocess
import threading
import os

def collect_monitor_logs(nodes):
    log_dir = "logs/monitor"
    os.makedirs(log_dir, exist_ok=True)

    def monitor_node(node):
        host, port = node["host"], str(node["port"])
        node_name = node["name"]
        outfile_path = os.path.join(log_dir, f"{node_name}_monitor.log")

        print(f"[+] Capturing MONITOR output for {node_name} at {host}:{port}")

        try:
            with open(outfile_path, "w") as f:
                process = subprocess.Popen(
                    ["redis-cli", "-h", host, "-p", port, "MONITOR"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                for line in process.stdout:
                    f.write(line)
                    f.flush()
        except Exception as e:
            print(f"[!] Error capturing MONITOR on {node_name}: {e}")

    threads = []
    for node in nodes:
        t = threading.Thread(target=monitor_node, args=(node,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
