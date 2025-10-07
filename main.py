# main.py
import os
from utils.node_loader import load_nodes

from parsers.monitor_parser import collect_monitor_logs

from parsers.acl_parser import  collect_acl_events
from parsers.slowlog_parser import parse_slowlog
from parsers.aof_parser import parse_aof_log
from parsers.redis_server_log_parser import parse_redislog
from parsers.rdb_parser import parse_rdb_logs
from parsers.memory_snapshot_parser import parse_snapshot

def display_menu():
    print("\n[ 🔍 Distributed Redis Forensic Parser ]")
    print("1. Load Cluster Topology")
    print("2. Live Capture: MONITOR")
    print("3. Live Capture: ACL Events")
    print("4. Parse: SLOWLOG Entries")
    print("5. Parse: AOF Commands")
    print("6. Parse: redis-server.log")
    print("7. Parse: RDB Snapshot")
    print("8. Parse: Memory Snapshot (.core)")
    print("9. Exit")

def main():
    config_path = "nodes.yaml"
    if not os.path.exists(config_path):
        print("⚠️  nodes.yaml not found. Please define your Redis cluster topology.")
        return

    nodes = load_nodes(config_path)

    while True:
        display_menu()
        choice = input("Select an option: ").strip()

        if choice == '1':
            print("\n[+] Loaded Redis Nodes:")
            for node in nodes:
                print(f" - {node['name']} at {node['host']}:{node['port']}")

        elif choice == '2':
            collect_monitor_logs(nodes)

        elif choice == '3':
            collect_acl_events(nodes)

        elif choice == '4':
            parse_slowlog(nodes)

        elif choice == '5':
            parse_aof_log(nodes)

        elif choice == '6':
            parse_redislog()

        elif choice == '7':
            parse_rdb_logs()

        elif choice == '8':
            snap_path = input("Enter memory snapshot path (e.g., redis.core): ")
            if os.path.exists(snap_path):
                parse_snapshot(snap_path)
            else:
                print("[!] File not found.")

        elif choice == '9':
            print("Exiting forensic parser.")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
