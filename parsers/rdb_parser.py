import os
from rdbtools import RdbParser, MemoryCallback
from utils.node_loader import load_nodes


class DataStructureRDBCallback(MemoryCallback):
    def __init__(self, output_file, selected_structures):
        super().__init__(stream=None, architecture=64)  # Fix: Pass dummy values
        self.output_file = output_file
        self.selected_structures = selected_structures
        self.entries = {
            "String": [],
            "Hash": [],
            "Set": [],
            "List": [],
            "SortedSet": []
        }

    def set(self, key, value, expiry, info):
        if "String" in self.selected_structures:
            self.entries["String"].append(f"{key} => {value} (Expiry: {expiry})")

    def hset(self, key, field, value):
        if "Hash" in self.selected_structures:
            self.entries["Hash"].append(f"{key}[{field}] = {value}")

    def sadd(self, key, member):
        if "Set" in self.selected_structures:
            self.entries["Set"].append(f"{key} {{+{member}}}")

    def rpush(self, key, value):
        if "List" in self.selected_structures:
            self.entries["List"].append(f"{key} -> {value}")

    def zadd(self, key, score, member):
        if "SortedSet" in self.selected_structures:
            self.entries["SortedSet"].append(f"{key} ({score}) -> {member}")

    def end_rdb(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as f:
            for dtype, lines in self.entries.items():
                if dtype in self.selected_structures:
                    f.write(f"--- {dtype} Entries ---\n")
                    for line in lines:
                        f.write(line + '\n')


def prompt_data_structure_selection():
    options = ['String', 'Hash', 'Set', 'List', 'SortedSet']
    print("\n[+] Select Redis data structures to recover from RDB:")
    for idx, opt in enumerate(options, 1):
        print(f"  {idx}. {opt}")
    print("  0. All")

    selection = input("Enter comma-separated choices (e.g., 1,3) or 0 for all: ").strip()
    if selection == '0':
        return set(options)

    selected = set()
    for s in selection.split(','):
        if s.strip().isdigit() and 1 <= int(s.strip()) <= len(options):
            selected.add(options[int(s.strip()) - 1])
    return selected


def parse_rdb_logs():
    nodes = load_nodes("nodes.yaml")
    selected_structures = prompt_data_structure_selection()

    print("\n[+] Extracting data structures:", ", ".join(selected_structures))

    for node in nodes:
        name = node["name"]
        rdb_path = node.get("rdb_path", f"/var/lib/redis/dump.rdb")
        output_path = f"logs/rdb/{name}_rdb_structures.txt"

        if not os.path.exists(rdb_path):
            print(f"[!] RDB file not found at: {rdb_path}")
            continue

        try:
            print(f"[→] Parsing RDB for node: {name}")
            callback = DataStructureRDBCallback(output_path, selected_structures)
            parser = RdbParser(callback)
            parser.parse(rdb_path)  # ✅ Pass string path
            print(f"[✓] Output saved to: {output_path}")
        except Exception as e:
            print(f"[✗] Failed to parse {rdb_path}: {e}")

