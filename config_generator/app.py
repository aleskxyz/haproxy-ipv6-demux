import ipaddress
import random
import subprocess
import os
import time
from jinja2 import Environment, FileSystemLoader
import signal
import sys

output_file = "haproxy/haproxy.cfg"
template_file = "haproxy.cfg.j2"

def signal_handler(sig, frame):
    print('SIGTERM received, shutting down.')
    sys.exit(0)

def get_env_var(var_name, default=None):
    return os.environ.get(var_name, default)

def generate_random_ipv6(subnet):
    try:
        network = ipaddress.IPv6Network(subnet)
        net_start = int(network.network_address)
        net_end = int(network.broadcast_address)
        return ipaddress.IPv6Address(random.randint(net_start, net_end))
    except ipaddress.AddressValueError:
        raise ValueError("Invalid subnet provided")

def check_template_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Template file not found: {file_path}")

signal.signal(signal.SIGTERM, signal_handler)

try:
    subnet = get_env_var("SUBNET")
    if subnet is None:
        raise ValueError("SUBNET environment variable must be set")
    ip_count = int(get_env_var("IP_COUNT", 100))
    interval = int(get_env_var("INTERVAL", 3600))
except Exception as e:
    print(e)
    exit(1)

while True:
    try:
        check_template_file_exists(template_file)
        random_ips = [str(generate_random_ipv6(subnet)) for _ in range(ip_count)]

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(template_file)
        rendered = template.render(ips=random_ips)

        with open(output_file, 'w') as file:
            file.write(rendered)

        print(f"Rendered content saved to {output_file}")

        subprocess.run(['docker-compose', '-p', 'haproxy-ipv6-demux', 'exec', 'haproxy', 'bash', '-c', 'kill -USR2 1'], check=True)
        print("HAProxy service reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reload HAProxy service: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

    time.sleep(interval)
