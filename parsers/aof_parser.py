# parsers/aof_parser.py

import os

def parse_aof_log(nodes):
    for node in nodes:
        name = node["name"]
        aof_path = node.get("aof_path", f"/var/lib/redis/{name}/appendonly.aof")
        output_path = f"logs/{name}_aof_parsed.txt"

        if not os.path.exists(aof_path):
            print(f"[!] AOF file not found for {name} at {aof_path}")
            continue

        try:
            with open(aof_path, "r") as f:
                lines = f.readlines()

            with open(output_path, "w") as out:
                for line in lines:
                    out.write(line)

            print(f"[✓] Parsed AOF log for {name} → {output_path}")
        except Exception as e:
            print(f"[!] Failed to read AOF for {name}: {e}")
