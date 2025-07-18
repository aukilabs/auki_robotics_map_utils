from utils.domain import Domain
import os, sys, time
import argparse
import yaml

def main(config):
    # Connect to Domain
    domain_server = Domain(config["domain"])
    ret, result = domain_server.auth()
    if not ret:
        print(result)
        sys.exit(1)

    original_waypoints, onmesh_waypoints = domain_server.optimize_route([{'x': 0, 'y': 0, 'z': 0.0}, {'x': 0, 'y': 0, 'z': 0.0}]) 
    print(original_waypoints    )
    print(onmesh_waypoints)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Domain Map")
    parser.add_argument('--config', type=str, help='Path to YAML config file', default='./config/default.yaml')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)
    main(config)