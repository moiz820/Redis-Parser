# memory_snapshot_parser.py

import os
import ast

# Simulated byte offset map
offset_map = {
    "SADD": 0x82AFFA7,
    "SET":  0x82AFFA7,
    "APPEND": 0x76AEF72,
    "HSET": 0x74A6F37,
    "HSETNX": 0x74A6F37
}

def parse_bytes_at_offset(file_path, offset, length=512):
    with open(file_path, 'rb') as f:
        f.seek(offset)
        data = f.read(length)
    return data.decode('utf-8', errors='ignore')

def parse_snapshot():
    snapshot_file = input("Enter memory snapshot filename (e.g., redis.core): ").strip()
    if not os.path.exists(snapshot_file):
        print(f"[!] File not found: {snapshot_file}")
        return

    for cmd, offset in offset_map.items():
        print(f"\n[+] Searching for command: {cmd} at offset 0x{offset:X}")
        try:
            result = parse_bytes_at_offset(snapshot_file, offset)
            print(f"→ Found: {result.strip()}")
        except Exception as e:
            print(f"[!] Failed to parse {cmd}: {e}")
