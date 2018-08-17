import sys
import os
import argparse

# Add parent directory to path to import general.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ../general.py
from general import *

TEST_NAME = "network"
CLIENT_NAME = "client-ngtcp2"
CLIENT_IMPLEMENTATION = "ngtcp2"
QUIC_RESULTS_DIR = "/root/quic-results"


def run_test_client(client_container_id, client_name, server_name, network_setting, resource):
    print("starting test client to test " + server_name)
    if client_container_id is None:
        print("cannot run test client, no container")
        exit(-1)
    command = "docker exec -i " + client_container_id + \
        " python /scripts/network/network-client-test.py --client " + client_name + \
        " --server " + server_name + " --network_setting " + network_setting + " --resource " + resource
    print("test client command: " + command)
    run_call_command(command)


def run_test_server(container_id, server_name, network_setting, resource):
    print("starting test server to test " + server_name)
    if container_id is None:
        print("cannot run server, no container")
        exit(-1)
    command = "docker exec -i -d " + container_id + " python -u /scripts/network/network-emu-server-test.py --server " + \
        server_name + " --network_setting " + network_setting + " --resource " + resource
    print("test server command: " + command)
    run_subprocess_command(command)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--amount_of_runs', help='Amount of times the compliance tests need to be run',
                        nargs='?', const=1, type=int, default=1)
    args = parser.parse_args()

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
    resources = [
        #"index.html",
        "large-text.txt",
        "image.jpg"
    ]

    remove_containers()
    client_container_id = None
    for x in range(0, args.amount_of_runs):
        update_start_time()
        for resource in resources:
            for implementation in implementations:
                for network_setting in network_settings:
                    container_id = create_server_container(TEST_NAME,
                        implementation)
                    client_container_id = restart_test_client(TEST_NAME,
                        CLIENT_IMPLEMENTATION, CLIENT_NAME, client_container_id, implementation)
                    run_test_server(container_id, implementation,
                        network_setting, resource)
                    run_test_client(client_container_id, CLIENT_IMPLEMENTATION,
                        implementation, network_setting, resource)
                    remove_container(container_id)
    remove_container(client_container_id)
    print("network test done")


if __name__ == "__main__":
  main()
