import sys
import os
import argparse

# Add parent directory to path to import general.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ../general.py
from general import *

TEST_NAME = "compliance"
CLIENT_NAME = "client-quicker"
CLIENT_IMPLEMENTATION = "quicker"
QUIC_RESULTS_DIR = "/Users/kevin/Documents/quic-results"


def run_test_client(client_container_id, server_name, branch):
    print("starting test client to test " + server_name)
    if client_container_id is None:
        print("cannot run test client, no container")
        exit(-1)
    command = "docker exec -i " + client_container_id + \
        " python /scripts/compliance/compliance-client-test.py --server " + \
        server_name + " --branch " + branch
    run_call_command(command)


def run_test_server(container_id, server_name, branch):
    print("starting test server to test " + server_name)
    if container_id is None:
        print("cannot run server, no container")
        exit(-1)
    command = "docker exec -i -d " + container_id + \
        " python -u /scripts/compliance/compliance-server-test.py --server " + \
        server_name + " --branch " + branch
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
    experiment_branches = [
        # Check if implementation works with a correct quicker
        "draft-12+PR#1389",
        # Quicker sents a badly formed frame
        "exp-badly-formed-frame",
        # Quicker sents data after fin bit was set on a stream
        "exp-data-after-fin",
        # Quicker sents all packets duplicate
        "exp-duplicate-packets",
        # Quicker sets its max_stream_data very low
        "exp-flow-control",
        # Quicker sents a lot of handshake packets in a single UDP datagram
        "exp-many-quic-in-udp",
        # Quicker sents packets reversed from the buffer
        "exp-out-of-order",
        # Quicker sents random bytes
        "exp-random-bytes",
        # Quicker requests a resource with HTTP on a Server unidirectional stream
        "exp-request-wrong-stream",
        # Quicker starts with a handshake packet instead of initial packet
        "exp-start-hs-frame",
        # Quicker sents a stop sending frame on a client unidirectional stream
        "exp-stop-sending-cli-uni",
    ]
    remove_containers()
    client_container_id = None
    for x in range(0, args.amount_of_runs):
        update_start_time()
        for implementation in implementations:
            for branch in experiment_branches:
                container_id = create_server_container(QUIC_RESULTS_DIR, TEST_NAME,
                                                       implementation)
                client_container_id = restart_test_client(QUIC_RESULTS_DIR, TEST_NAME,
                                                          CLIENT_IMPLEMENTATION, CLIENT_NAME, client_container_id, implementation)
                run_test_server(container_id, implementation, branch)
                run_test_client(client_container_id, implementation, branch)
                remove_container(container_id)
    remove_container(client_container_id)
    print("compliance test done")


if __name__ == "__main__":
  main()
