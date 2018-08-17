import subprocess
import argparse
import signal
import sys

TEST_NAME = "performance"

QUIC_EVALUATION_DIR = "/root/quic-evaluation"
QUIC_RESULTS_DIR = "/root/quic-results"

tcpdump_process = None
out_file = None

def run_test_server(container_id, server_name, amount, resource):
    if container_id is None:
        print("cannot run server, no container")
        exit(-1)
    command = "docker exec -i -d " + container_id + \
        " python -u " + QUIC_EVALUATION_DIR + "/scripts/performance/performance-server-test.py --server " + \
        server_name + " --amount " + amount + " --resource " + resource
    print("test server command: " + command)
    run_subprocess_command(command)

def run_command(command, stdout=None, stderr=None):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server, amount, resource):
    command = "tcpdump -i any -s0 udp port 4433 -U -w " + QUIC_RESULTS_DIR + "/tcpdump/" + \
         server + "-" + amount + "-" + resource + ".pcap"
    return subprocess.Popen(command.split())

def start_docker_monitor(container_id, server, amount, resource):
    command = "python " + QUIC_EVALUATION_DIR + "/scripts/monitor/monitor-docker.py --container " + container_id + \
        "--path " + QUIC_RESULTS_DIR + "/monitor --file " + server + "-" + amount + "-" + resource + ".csv"
    return subprocess.Popen(command.split())


def sigterm_handler(signal, frame):
    global tcpdump_process
    global out_file
    print("server done")
    if out_file is not None:
        out_file.flush()
        out_file.close()
    if tcpdump_process is not None:
        tcpdump_process.send_signal(signal.SIGINT)
    sys.exit(0)


def main():
    global tcpdump_process
    global out_file

    signal.signal(signal.SIGTERM, sigterm_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--server', help='Server name that is tested with this client script', required=True)
    parser.add_argument(
        '-a', '--amount', help='Amount of connections to open', required=True, default=1, type=int)
    parser.add_argument(
        '-r', '--resource', help='Resource that is going to be requested by the client', required=True)

    args = parser.parse_args()

    out_file = open(QUIC_RESULTS_DIR + "/logs/" + args.server + "-" + args.amount + "-" + args.resource + ".txt", "w+")
    tcpdump_process = start_tcpdump(args.server, args.amount, args.resource)
    container_id = create_server_container(TEST_NAME, args.server)
    start_docker_monitor(container_id, args.server, args.amount, args.resource)
    run_test_server(container_id, args.server, args.amount, args.resource)


if __name__ == "__main__":
  main()
