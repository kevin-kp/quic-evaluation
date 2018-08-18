import subprocess
import argparse
import signal
import sys
import os

# Add parent directory to path to import general.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ../general.py
from general import *

TEST_NAME = "performance"

QUIC_EVALUATION_DIR = "/root/quic-evaluation"
QUIC_RESULTS_DIR = "/root/quic-results"

tcpdump_process = None

def run_test_server(container_id, server_name, amount, resource):
    if container_id is None:
        print("cannot run server, no container")
        exit(-1)
    command = "docker exec -i " + container_id + \
        " python -u /scripts/performance/performance-server-test.py --server " + \
        server_name + " --amount " + str(amount) + " --resource " + resource
    print("test server command: " + command)
    run_command(command)

def run_command(command, stdout=None, stderr=None):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server, amount, resource):
    command = "tcpdump -i any -s0 udp port 4433 -U -w " + QUIC_RESULTS_DIR + "/tcpdump/" + \
         server + "-" + str(amount) + "-" + resource + ".pcap"
    return subprocess.Popen(command.split())

def start_docker_monitor(container_id, server, amount, resource):
    command = "python " + QUIC_EVALUATION_DIR + "/scripts/monitor/monitor-docker.py --container " + container_id + \
        " --path " + QUIC_RESULTS_DIR + "/monitor --file " + server + "-" + str(amount) + "-" + resource + ".csv"
    return subprocess.Popen(command.split())


def sigterm_handler(signal, frame):
    global tcpdump_process
    print("server done")
    if tcpdump_process is not None:
        tcpdump_process.send_signal(signal.SIGINT)
    sys.exit(0)


def main():
    global tcpdump_process

    signal.signal(signal.SIGTERM, sigterm_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--server', help='Server name that is tested with this client script', required=True)
    parser.add_argument(
        '-a', '--amount', help='Amount of connections to open', required=True, default=1, type=int)
    parser.add_argument(
        '-r', '--resource', help='Resource that is going to be requested by the client', required=True)

    args = parser.parse_args()

    remove_containers()
    tcpdump_process = None
    container_id = None
    monitor_process = None
    try:
        tcpdump_process = start_tcpdump(args.server, args.amount, args.resource)
        container_id = create_server_container(QUIC_RESULTS_DIR, TEST_NAME, args.server)
        monitor_process = start_docker_monitor(container_id, args.server, args.amount, args.resource)
        run_test_server(container_id, args.server, args.amount, args.resource)
    except KeyboardInterrupt:
        print("keyboard interrupt")
        # clean up
        if tcpdump_process is not None:
            tcpdump_process.send_signal(signal.SIGINT)
        if monitor_process is not None:
            monitor_process.send_signal(signal.SIGINT)
        if container_id is not None:
            remove_container(container_id)


if __name__ == "__main__":
  main()
