from utils.domain import Domain
import sys
import argparse
import yaml

# Pose is to be passed as a transformation matrix, for example:
pose =  [
    [-9.99998084e-01,  0.00000000e+00, -1.95768216e-03, -2.32179699e+00],
    [ 0.00000000e+00, -1.00000000e+00,  0.00000000e+00,  6.75000000e-01],
    [-1.95768216e-03,  0.00000000e+00,  9.99998084e-01,  2.71694765e-01],
    [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000000e+00]
]

def main(config):
    # Connect to Domain
    domain_server = Domain(config["domain"])
    ret, result = domain_server.auth()
    if not ret:
        print(result)
        sys.exit(1)

    domain_server.get_raycast(pose)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Raycast as a service")
    parser.add_argument('--config', type=str, help='Path to YAML config file', default='./config/default.yaml')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)
    main(config)