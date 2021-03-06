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


def get_network_settings(network_settings_name):
    network_settings = {
        # Google chrome throttling setting: WiFi
        "wifi": {
            "name": "wifi",
            "latency": "2ms",
            "jitter": None,
            "loss": None,
            "bandwidth": "29Mbit",
            "bandwidth_burst": "130kb"
        },
        # Google chrome throttling setting: WiFi with higher latency and loss
        "wifi_transatlantic_loss": {
            "name": "wifi_transatlantic_loss",
            "latency": "75ms",
            "jitter": "5ms",
            "loss": "0.2%",
            "bandwidth": "29Mbit",
            "bandwidth_burst": "130kb"
        },
        # Google chrome throttling setting: 4G
        "4g": {
            "name": "4g",
            "latency": "20ms",
            "jitter": "4ms",
            "loss": None,
            "bandwidth": "4.0Mbit",
            "bandwidth_burst": "64kb"
        },
        # Google chrome throttling setting: 2G with loss
        "2g_loss": {
            "name": "2g_loss",
            "latency": "150ms",
            "jitter": "20ms",
            "loss": "1.2%",
            "bandwidth": "450kbit",
            "bandwidth_burst": "40kb"
        }
    }
    return network_settings.get(network_settings_name)

def get_network_settings_array(network_settings_name):
    network_settings = get_network_settings(network_settings_name)
    network_settings_array = [
        network_settings["bandwidth"],
        network_settings["bandwidth_burst"],
        network_settings["latency"],
    ]
    if network_settings["jitter"] is not None:
        network_settings_array.append(network_settings["jitter"])
    if network_settings["loss"] is not None:
        network_settings_array.append(network_settings["loss"])

    return network_settings_array

def activate_network_emulation(network_settings_name):
    network_settings = get_network_settings(network_settings_name)
    first_command = "tc qdisc add dev eth0 root handle 1 tbf rate {0} burst {1} latency 50ms"
    second_command = "tc qdisc add dev eth0 parent 1: handle 2: netem delay {0}"
    i = 1
    if network_settings["jitter"] is not None:
        second_command += " {" + str(i) +"} distribution normal"
        i = i + 1

    if network_settings["loss"] is not None:
        second_command += " loss {" + str(i) +"} "

    networks_array = get_network_settings_array(network_settings_name)
    first_command_array = networks_array[:2]
    second_command_array = networks_array[2:]
    
    first_command = first_command.format(*first_command_array)
    second_command = second_command.format(*second_command_array)
    
    run_command(first_command)
    run_command(second_command)

def run_command(command, stdout=None, stderr=None):
    subprocess.call(command.split(), stdout=stdout, stderr=stderr)


def start_tcpdump(server, network_settings_name, resource):
    command = "tcpdump -i any -s0 udp port 4433 -U -w /logs/" + \
        server + "-" + network_settings_name + "-" + resource + ".pcap"
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
        '-n', '--network_setting', help='Network settings name that is going to be used to emulate network to test the server', required=True)
    parser.add_argument(
        '-r', '--resource', help='Resource that is going to be requested (logging purposes)', required=True)

    args = parser.parse_args()

    run_server_command = get_run_test_server_command(args.server)

    if run_server_command is None:
        print("unknown server")
        exit(-1)

    out_file = open("/logs/" + args.server + "-" + args.network_setting + "-" + args.resource + ".txt", "w+")
    tcpdump_process = start_tcpdump(args.server, args.network_setting, args.resource)
    activate_network_emulation(args.network_setting)
    run_command(run_server_command, stdout=out_file, stderr=out_file)


if __name__ == "__main__":
  main()
