#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, struct, string
from utils.node_loader import load_nodes   # <--- integrated here

# ---- RDB constants ----
RDB_OPCODE_AUX           = 0xFA
RDB_OPCODE_RESIZEDB      = 0xFB
RDB_OPCODE_EXPIRETIME_MS = 0xFC
RDB_OPCODE_EXPIRETIME    = 0xFD
RDB_OPCODE_SELECTDB      = 0xFE
RDB_OPCODE_EOF           = 0xFF

RDB_TYPE_STRING          = 0x00
RDB_TYPE_SET             = 0x02
RDB_TYPE_LIST_ZIPLIST    = 0x0A
RDB_TYPE_SET_INTSET      = 0x0B
RDB_TYPE_ZSET_ZIPLIST    = 0x0C
RDB_TYPE_HASH_ZIPLIST    = 0x0D
RDB_TYPE_LIST_QUICKLIST  = 0x0E

# Redis 7 / RDB v10 new listpack types
RDB_TYPE_HASH_LISTPACK       = 0x10
RDB_TYPE_ZSET_LISTPACK       = 0x11
RDB_TYPE_LIST_QUICKLIST_2    = 0x12
RDB_TYPE_STREAM_LISTPACKS_2  = 0x13
RDB_TYPE_SET_LISTPACK        = 0x14

TYPE_NAMES = {
    RDB_TYPE_STRING: "string",
    RDB_TYPE_SET: "set",
    RDB_TYPE_LIST_ZIPLIST: "list-ziplist",
    RDB_TYPE_SET_INTSET: "set-intset",
    RDB_TYPE_ZSET_ZIPLIST: "zset-ziplist",
    RDB_TYPE_HASH_ZIPLIST: "hash-ziplist",
    RDB_TYPE_LIST_QUICKLIST: "list-quicklist",
    RDB_TYPE_HASH_LISTPACK: "hash-listpack",
    RDB_TYPE_ZSET_LISTPACK: "zset-listpack",
    RDB_TYPE_LIST_QUICKLIST_2: "list-quicklist2",
    RDB_TYPE_STREAM_LISTPACKS_2: "stream-listpacks2",
    RDB_TYPE_SET_LISTPACK: "set-listpack",
}

PRINTABLE = set(bytes(string.printable, "ascii"))

# ---------------- helpers ----------------

def safe(b, i, n=1):
    return 0 <= i and i + n <= len(b)

def read_length(b, i):
    first = b[i]
    enc = (first & 0xC0) >> 6
    if enc == 0:   # 6-bit
        return (first & 0x3F, i+1, False)
    elif enc == 1: # 14-bit
        val = ((first & 0x3F) << 8) | b[i+1]
        return (val, i+2, False)
    elif enc == 2: # 32-bit
        val = struct.unpack(">I", b[i+1:i+5])[0]
        return (val, i+5, False)
    else:          # special encoding (int/LZF)
        return (first & 0x3F, i+1, True)

def read_string(b, i, raw=False):
    length, i, encoded = read_length(b, i)
    if not encoded:
        if not safe(b, i, length): raise IndexError("string OOB")
        data = b[i:i+length]
        return (data if raw else data.decode(errors="ignore"), i+length)
    enc_type = length
    if enc_type == 0:  # 8-bit int
        val = b[i] if b[i] < 128 else b[i]-256
        return (str(val), i+1)
    elif enc_type == 1: # 16-bit int
        val = struct.unpack(">h", b[i:i+2])[0]; return (str(val), i+2)
    elif enc_type == 2: # 32-bit int
        val = struct.unpack(">i", b[i:i+4])[0]; return (str(val), i+4)
    elif enc_type == 3: # LZF compressed (stub)
        clen, i, _ = read_length(b, i)
        ulen, i, _ = read_length(b, i)
        return (f"[LZF {ulen} bytes]", i+clen)
    else:
        return ("[unknown-encoding]", i)

def listpack_extract_printables(lp_blob):
    if not isinstance(lp_blob, (bytes, bytearray)) or len(lp_blob) < 7:
        return []
    out, p = [], 6
    end_pos = lp_blob.find(b'\xFF', 6)
    if end_pos == -1: end_pos = len(lp_blob)
    while p < end_pos:
        if lp_blob[p] in PRINTABLE:
            start = p
            while p < end_pos and lp_blob[p] in PRINTABLE:
                p += 1
            token = lp_blob[start:p].decode(errors="ignore").strip()
            if token: out.append(token)
        else:
            p += 1
    return out

def to_hash_dict(vals):
    return {vals[i]: vals[i+1] for i in range(0, len(vals)-1, 2)}

# ---------------- main parser ----------------

def parse_rdb(path):
    with open(path, "rb") as f:
        data = f.read()

    header = data[0:9].decode(errors="ignore")
    print(f"Header: {header}")

    i = data.find(b'\xfe')  # SELECTDB
    if i == -1:
        print("No SELECTDB found")
        return
    dbnum = data[i+1] if safe(data, i+1) else 0
    print(f"First SELECTDB at offset {hex(i)} (DB {dbnum})")
    i += 2

    while i < len(data):
        if not safe(data, i): break
        op = data[i]

        if op == RDB_OPCODE_EOF:
            print(f"EOF at offset {hex(i)}")
            break

        if op == RDB_OPCODE_RESIZEDB:
            start = i
            i += 1
            size1, i, _ = read_length(data, i)
            size2, i, _ = read_length(data, i)
            print(f"RESIZEDB at offset {hex(start)} (hash_table={size1}, expires_table={size2})")
            continue

        if op in TYPE_NAMES:
            tname = TYPE_NAMES[op]
            start_off = i
            i += 1
            key, i = read_string(data, i)
            print(f"Opcode {op} ({tname}) at offset {hex(start_off)}")
            if key is None: key = ""

            if op == RDB_TYPE_STRING:
                val, i = read_string(data, i)
                print(f"  Key={key} | Type=string | Value={val}")

            elif op == RDB_TYPE_LIST_QUICKLIST_2:
                value_start = i
                next_pos = None
                j = value_start
                while j < len(data) - 2:
                    candidate = data[j]
                    if candidate in TYPE_NAMES:
                        try:
                            test_key, _ = read_string(data, j+1)
                            if isinstance(test_key, str) and test_key and all(ch in string.printable for ch in test_key):
                                next_pos = j
                                break
                        except Exception:
                            pass
                    elif candidate == RDB_OPCODE_EOF:
                        if j > len(data) - 16:
                            next_pos = j
                            break
                    j += 1
                value_end = next_pos if next_pos else len(data)
                chunk = data[value_start:value_end]
                vals = listpack_extract_printables(chunk)
                print(f"  Key={key} | Type=list-quicklist2 | Values={vals}")
                i = value_end

            elif op == RDB_TYPE_HASH_LISTPACK:
                blob, i = read_string(data, i, raw=True)
                vals = listpack_extract_printables(blob)
                print(f"  Key={key} | Type=hash-listpack | Values={to_hash_dict(vals)}")

            elif op == RDB_TYPE_ZSET_LISTPACK:
                blob, i = read_string(data, i, raw=True)
                vals = listpack_extract_printables(blob)
                d = {}
                for k in range(0, len(vals)-1, 2):
                    try:
                        d[vals[k]] = float(vals[k+1])
                    except:
                        d[vals[k]] = vals[k+1]
                print(f"  Key={key} | Type=zset-listpack | Values={d}")

            elif op == RDB_TYPE_SET_LISTPACK:
                blob, i = read_string(data, i, raw=True)
                vals = listpack_extract_printables(blob)
                print(f"  Key={key} | Type=set-listpack | Values={vals}")

            else:
                blob, i = read_string(data, i, raw=True)
                vals = listpack_extract_printables(blob)
                print(f"  Key={key} | Type={tname} | Values={vals}")

        else:
            i += 1
def parse_rdb_logs():
    rdb_path = input("Enter RDB file path (leave empty to auto-load from nodes.yaml): ").strip()
    if rdb_path:
        # Parse single file
        if os.path.exists(rdb_path):
            parse_rdb(rdb_path)
        else:
            print(f"[!] File not found: {rdb_path}")
    else:
        # Auto-load from nodes.yaml
        nodes = load_nodes()
        for node in nodes:
            rdb_path = f"logs/{node['name']}/dump.rdb"
            print(f"\n[+] Parsing RDB for node: {node['name']} ({rdb_path})")
            try:
                parse_rdb(rdb_path)
            except FileNotFoundError:
                print(f"⚠️  RDB file not found for {node['name']} at {rdb_path}")


# ---- Run ----

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # run on single file
        parse_rdb(sys.argv[1])
    else:
        # run on all nodes from nodes.yaml
        nodes = load_nodes()
        for node in nodes:
            rdb_path = f"logs/{node['name']}/dump.rdb"
            print(f"\n[+] Parsing RDB for node: {node['name']} ({rdb_path})")
            try:
                parse_rdb(rdb_path)
            except FileNotFoundError:
                print(f"⚠️  RDB file not found for {node['name']} at {rdb_path}")
