import sys
import os

# Add parent directory to path to import general.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ../general.py
from general import *

TEST_NAME = "network"


def run_test_client(client_container_id, server_name, network_setting):
    print("starting test client to test " + server_name)
    if client_container_id is None:
        print("cannot run test client, no container")
        exit(-1)
    command = "docker exec -i " + client_container_id + \
        " python /scripts/network/network-client-test.py --server " + \
        server_name + " --networksetting " + network_setting
    run_call_command(command)


def run_test_server(container_id, server_name, network_setting):
    print("starting test server to test " + server_name)
    if container_id is None:
        print("cannot run server, no container")
        exit(-1)
    command = "docker exec -i -d " + container_id + \
        " python -u /scripts/network/network-server-test.py --server " + \
        server_name + " --networksetting " + network_setting
    run_subprocess_command(command)


def main():
    implementations = [
        "ngtcp2",
        "quicker",
        "quant"
    ]

    network_settings = [
        "wifi",
        "wifi_transatlantic_loss",
        "4g",
        "2g_loss"
    ]
    
    remove_containers()
    client_container_id = None
    for implementation in implementations:
        for network_setting in network_settings:
            container_id = create_server_container(TEST_NAME, implementation)
            client_container_id = restart_test_client(
                TEST_NAME, client_container_id, implementation)
            run_test_server(container_id, implementation, network_setting)
            run_test_client(client_container_id, implementation, network_setting)
            remove_container(container_id)
    print("network test done")

if __name__ == "__main__":
  main()
