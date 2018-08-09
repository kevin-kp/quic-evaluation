import subprocess
import argparse


def get_run_test_server_command(servername):
    switcher = {
        #"ats": "??",
        "ngtcp2": "/ngtcp2/examples/server 0.0.0.0 4433 /keys/domain.key /keys/domain.crt",
        "picoquic": "/picoquic/picoquicdemo -c /keys/domain.crt -k /keys/domain.key -p 4433",
        "quicker": "sh /server/scripts/run-scripts/server/build_quicker_and_run.sh 0.0.0.0 4433 /keys/domain.key /keys/domain.crt",
        "quant": "/quant/bin/server -d / -i eth0 -p 4433:4433/udp -k /keys/domain.key -c /keys/domain.crt",
    }
    return switcher.get(servername, None)

def run_command(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server, branch):
    command = "tcpdump -i eth0 -s0 udp port 4433 -w /logs/" + server + "-" + branch + ".pcap"
    return subprocess.Popen(command.split())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--server', help='Server name that is tested with this client script', required=True)
    parser.add_argument('-b','--branch', help='Branch that is going to be used to test the server (only for logging purpose, but still required though)', required=True)

    args = parser.parse_args()

    run_server_command = get_run_test_server_command(args.server)

    if run_server_command is None:
        print("unknown server")
        exit(-1)

    with open("/logs/" + args.server + "-" + args.branch + ".txt","w+") as out:
        tcpdump_process = start_tcpdump(args.server, args.branch)
        run_command(run_server_command, stdout=out)
        tcpdump_process.kill()

if __name__== "__main__":
  main()