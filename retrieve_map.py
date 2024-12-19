from utils.domain import Domain
import os, sys, time
import argparse
import yaml

def main(config, image_format, resolution):
    # Connect to Domain
    domain_server = Domain(config["domain"])
    ret, result = domain_server.auth()
    if not ret:
        print(result)
        sys.exit(1)

    domain_server.get_map(image_format=image_format, resolution=resolution)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Domain Map")
    parser.add_argument('--config', type=str, help='Path to YAML config file', default='./config/default.yaml')
    parser.add_argument(
        '--image-format', 
        type=str, 
        help='Image format to save. Options: "png" (default), "bmp", or "pgm".', 
        choices=['png', 'bmp', 'pgm'], 
        default='png'
    )
    parser.add_argument('--resolution', type=int, help='Pixels per meter', default=20)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)
    main(config, args.image_format, args.resolution)
