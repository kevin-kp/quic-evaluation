import subprocess
import argparse
import signal


def run_command(command, stdout=None, stderr=None):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server, network_settings_name):
    command = "tcpdump -i any -s0 udp port 4433 -U -w /logs/" + server + "-" + network_settings_name + ".pcap"
    return subprocess.Popen(command.split())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--server', help='Server name that is tested with this client script', required=True)
    parser.add_argument(
        '-n', '--networksetting', help='Network settings name that is going to be used to emulate network to test the server (for logging purposes)', required=True)

    args = parser.parse_args()

    run_quicker_client = "sh ./scripts/run-scripts/client/build_quicker_and_run.sh " + args.server + " 4433"

    with open("/logs/" + args.server + "-" + args.networksetting + ".txt","w+") as out:
        tcpdump_process = start_tcpdump(args.server, args.networksetting)
        run_command(run_quicker_client, stdout=out)
        tcpdump_process.send_signal(signal.SIGINT)

if __name__== "__main__":
  main()