import subprocess
import argparse
import signal
import sys

tcpdump_process = None
out_file = None


def get_run_test_server_command(servername):
    switcher = {
        #"ats": "??",
        "ngtcp2": "/ngtcp2/examples/server 0.0.0.0 4433 /keys/domain.key /keys/domain.crt -d /www",
        "picoquic": "/picoquic/picoquicdemo -c /keys/domain.crt -k /keys/domain.key -p 4433",
        "quicker": "sh /server/scripts/run-scripts/server/build_quicker_and_run.sh 0.0.0.0 4433 /keys/domain.key /keys/domain.crt",
        "quant": "/quant/Debug/bin/server -d /www -i eth0 -p 4433:4433/udp -k /keys/domain.key -c /keys/domain.crt",
    }
    return switcher.get(servername, None)

def run_command(command, stdout=None, stderr=None):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server):
    command = "tcpdump -i any -s0 udp port 4433 -U -w /logs/" + \
        server + "-real-network.pcap"
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

    args = parser.parse_args()

    run_server_command = get_run_test_server_command(args.server)

    if run_server_command is None:
        print("unknown server")
        exit(-1)

    out_file = open("/logs/" + args.server + "-real-network.txt", "w+")
    tcpdump_process = start_tcpdump(args.server)
    run_command(run_server_command, stdout=out_file, stderr=out_file)


if __name__ == "__main__":
  main()
