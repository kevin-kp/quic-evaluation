import sys
import os
import argparse
import subprocess
import signal

# Add parent directory to path to import general.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ../general.py
from general import *

TEST_NAME = "performance"
CLIENT_NAME = "client-ngtcp2"
CLIENT_IMPLEMENTATION = "ngtcp2"
QUIC_RESULTS_DIR = "/root/quic-results"


def run_test_client(client_container_id, client_name, server_name, amount, resource):
    print("starting test client to test " + server_name)
    if client_container_id is None:
        print("cannot run test client, no container")
        exit(-1)
    command = "docker exec -i " + client_container_id + \
        " python /scripts/performance/performance-client-test.py --client " + client_name + \
        " --server " + server_name + " --name " + server_name + " --amount " + str(amount) + " --resource " + resource
    print("test client command: " + command)
    run_call_command(command)


def run_test_server(server_name, amount, resource):
    print("starting test server to test " + server_name)
    command = "python -u /scripts/performance/start-docker-server.py --server " + \
        server_name + " --amount " + str(amount) + " --resource " + resource
    print("test server command: " + command)
    return run_subprocess(command)

def run_subprocess(command):
    return subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--amount_of_runs', help='Amount of times the compliance tests need to be run',
                        nargs='?', const=1, type=int, default=1)
    args = parser.parse_args()

    implementations = [
        "ngtcp2",
        "quicker",
        "quicly"
    ]

    amounts = [5, 10, 15, 20, 30, 40, 50, 75, 100, 150, 200]
    resources = [
        "index.html",
    ]

    remove_containers()
    client_container_id = None
    for x in range(0, args.amount_of_runs):
        update_start_time()
        for resource in resources:
            for implementation in implementations:
                for amount in amounts:
                    #container_id = create_server_container(QUIC_RESULTS_DIR,TEST_NAME,implementation)
                    client_container_id = restart_test_client(QUIC_RESULTS_DIR,TEST_NAME,
                        CLIENT_IMPLEMENTATION, CLIENT_NAME, client_container_id, implementation)
                    process = run_test_server(implementation,
                        amount, resource)
                    run_test_client(client_container_id, CLIENT_IMPLEMENTATION,
                        implementation, amount, resource)
                    process.send_signal(signal.SIGINT)
                    #remove_container(container_id)
    remove_container(client_container_id)
    print("network test done")


if __name__ == "__main__":
  main()
