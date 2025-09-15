import yaml

def load_nodes(yaml_path="nodes.yaml"):
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    return config.get("nodes", [])
