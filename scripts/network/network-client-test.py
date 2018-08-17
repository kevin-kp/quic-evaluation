import subprocess
import argparse
import signal
import os

def get_run_test_client_command(clientname, servername, resource):
    if clientname == "ngtcp2":
        if not os.path.exists("/data"):
            os.makedirs("/data")
        f = open("/data/" + resource, "w+")
        f.write("GET /" + resource + "\n")
        f.flush()
        f.close()
    switcher = {
        #"ats": "??",
        "ngtcp2": "/ngtcp2/examples/client " + servername + " 4433 -d /data/" + resource,
        #"picoquic": "??",
        "quicker": "sh ./scripts/run-scripts/client/build_quicker_and_run.sh " + servername + " 4433 " + resource,
        #"quant": "??",
    }
    return switcher.get(servername, None)


def run_command(command, stdout=None, stderr=None):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server, network_settings_name, resource):
    command = "tcpdump -i any -s0 udp port 4433 -U -w /logs/" + \
        server + "-" + network_settings_name + "-" + resource + ".pcap"
    return subprocess.Popen(command.split())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--client', help='Client name that is used to test the server', required=True)
    parser.add_argument(
        '-s', '--server', help='Server name that is tested with this client script', required=True)
    parser.add_argument(
        '-n', '--network_setting', help='Network settings name that is going to be used to emulate network to test the server (for logging purposes)', required=True)
    parser.add_argument(
        '-r', '--resource', help='Resource that is requested', required=True)

    args = parser.parse_args()

    run_client_command = get_run_test_client_command(args.client, args.server, args.resource)

    with open("/logs/" + args.server + "-" + args.network_setting + "-" + args.resource + ".txt", "w+") as out:
        tcpdump_process = start_tcpdump(
            args.server, args.network_setting, args.resource)
        run_command(run_client_command, stdout=out, stderr=out)
        tcpdump_process.send_signal(signal.SIGINT)


if __name__ == "__main__":
  main()
