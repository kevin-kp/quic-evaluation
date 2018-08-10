import subprocess
import argparse
import signal


def run_command(command, stdout=None, stderr=None):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server, branch):
    command = "tcpdump -i any -s0 udp port 4433 -U -w /logs/" + server + "-" + branch + ".pcap"
    return subprocess.Popen(command.split())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--server', help='Server name that is tested with this client script', required=True)
    parser.add_argument('-b','--branch', help='Branch that is going to be used to test the server', required=True)

    args = parser.parse_args()

    run_quicker_client = "sh ./scripts/run-scripts/client/build_quicker_and_run.sh " + args.server + " 4433"

    with open("/logs/" + args.server + "-" + args.branch + ".txt","w+") as out:
        run_command("git checkout " + args.branch)
        tcpdump_process = start_tcpdump(args.server, args.branch)
        run_command(run_quicker_client, stdout=out)
        tcpdump_process.send_signal(signal.SIGINT)

if __name__== "__main__":
  main()