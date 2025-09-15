# main.py
import yaml
import os
from utils.node_loader import load_nodes_from_yaml
from parsers.monitor_collector import collect_monitor_logs
from parsers.acl_collector import collect_acl_events
from parsers.slowlog_parser import parse_slowlog
from parsers.aof_parser import parse_aof_log
from parsers.redislog_parser import parse_redislog
from analysis.correlate import correlate_node_logs  # NEW IMPORT

def display_menu():
    print("\n[ Distributed Redis Forensic Parser ]")
    print("1. Load cluster topology")
    print("2. Collect MONITOR logs (live)")
    print("3. Capture ACL events")
    print("4. Parse SLOWLOG entries")
    print("5. Parse AOF commands")
    print("6. Parse redis-server.log")
    print("7. Correlate and analyze forensic logs")  # NEW OPTION
    print("8. Exit")

def correlate_logs(nodes):
    print("\n[🔍 Forensic Correlation Started]")
    for node in nodes:
        correlate_node_logs(node["name"])
    print("[✅ Correlation completed for all nodes]")

def main():
    config_path = "nodes.yaml"
    if not os.path.exists(config_path):
        print("nodes.yaml not found. Please define your Redis cluster topology.")
        return

    nodes = load_nodes_from_yaml(config_path)

    while True:
        display_menu()
        choice = input("Select an option: ").strip()

        if choice == '1':
            print("\n[+] Loaded Redis nodes:")
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
            parse_redislog(nodes)

        elif choice == '7':
            correlate_logs(nodes)

        elif choice == '8':
            print("Exiting.")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
