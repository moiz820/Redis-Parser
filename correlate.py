import os
import json
from datetime import datetime

LOG_DIR = "logs/"

def load_log(file_name):
    path = os.path.join(LOG_DIR, file_name)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def correlate_node_logs(node_name):
    print(f"\n🔍 Correlating logs for node: {node_name}")

    monitor_logs = load_log(f"{node_name}_monitor_acl_log.txt")
    aof_logs = load_log(f"{node_name}_aof_log.txt")
    slow_logs = load_log(f"{node_name}_slowlog.txt")
    server_logs = load_log(f"{node_name}_redis_server_parsed.txt")

    timeline = []

    # Merge logs by timestamp (where possible)
    for log in monitor_logs:
        if "MONITOR" in log:
            timeline.append(("monitor", log))
        elif "ACL" in log:
            timeline.append(("acl", log))

    for log in aof_logs:
        timeline.append(("aof", log))
    for log in slow_logs:
        timeline.append(("slowlog", log))
    for log in server_logs:
        timeline.append(("server", log))

    # Optional: Sort if timestamps are consistent (you can enhance with regex later)
    timeline.sort(key=lambda x: x[1][:30])  # crude sort by line prefix

    output_path = os.path.join(LOG_DIR, f"{node_name}_correlation_report.txt")
    with open(output_path, "w") as out:
        out.write(f"=== Forensic Timeline Correlation for {node_name} ===\n")
        for source, entry in timeline:
            out.write(f"[{source.upper()}] {entry}\n")

    print(f"✅ Correlation completed for {node_name}. Report saved to {output_path}")

def run_all_correlation():
    with open("nodes.json", "r") as f:
        nodes = json.load(f)
    for node in nodes:
        correlate_node_logs(node["name"])

if __name__ == "__main__":
    run_all_correlation()
