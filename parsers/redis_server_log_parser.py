import os
import re
from utils.node_loader import load_nodes

def parse_redislog():
    nodes = load_nodes()

    patterns = {
        "authentication": re.compile(r"Authenticated .*?"),
        "config_change": re.compile(r"CONFIG SET .*"),
        "error": re.compile(r"\*\*\* WARNING .*"),
        "startup": re.compile(r"Server started, Redis version .*"),
        "replication": re.compile(r"(Connecting to MASTER|MASTER <-> REPLICA sync started)")
    }

    for node in nodes:
        name = node["name"]
        log_path = node.get("server_log_path", f"/var/log/redis/redis-server.log")
        output_path = f"logs/{name}_redis_server_parsed.txt"

        if not os.path.exists(log_path):
            print(f"[redis-server.log] Log file not found for {name} at {log_path}")
            continue

        try:
            with open(log_path, 'r') as infile, open(output_path, 'w') as outfile:
                outfile.write(f"=== Parsed Redis Server Log for {name} ===\n")
                for line in infile:
                    for label, pattern in patterns.items():
                        if pattern.search(line):
                            outfile.write(f"[{label.upper()}] {line.strip()}\n")
            print(f"[redis-server.log] Log parsed for {name}. Output saved to {output_path}")
        except Exception as e:
            print(f"[redis-server.log] Failed to parse {log_path}: {e}")
