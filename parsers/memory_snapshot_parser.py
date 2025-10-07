# memory_snapshot_parser.py

import os
import ast

# Simulated byte offset map
offset_map = {
    # String commands
    "SET":        0x82AFFA7,
    "GET":        0x82AFAB1,
    "APPEND":     0x76AEF72,
    "GETDEL":     0x76AEF99,
    "MGET":       0x76AEFBA,

    # Hash commands
    "HSET":       0x74A6F37,
    "HSETNX":     0x74A6F37,
    "HGET":       0x74A6F49,
    "HGETALL":    0x74A6F62,
    "HDEL":       0x74A6F75,

    # List commands
    "LPUSH":      0x71DFE12,
    "RPUSH":      0x71DFE29,
    "LPOP":       0x71DFE44,
    "RPOP":       0x71DFE58,
    "LSET":       0x71DFE72,
    "LRANGE":     0x71DFE85,
    "LREM":       0x71DFE98,

    # Set commands
    "SADD":       0x82AFFA7,
    "SREM":       0x82AFFC0,
    "SMEMBERS":   0x82AFFD2,
    "SSCAN":      0x82AFFE9,

    # Sorted set commands
    "ZADD":       0x7F5AF10,
    "ZREM":       0x7F5AF24,
    "ZRANGE":     0x7F5AF3D,
    "ZSCAN":      0x7F5AF52
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
