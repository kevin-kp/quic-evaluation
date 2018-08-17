import subprocess
import argparse
import signal
import os
import threading

LOCAL_PATH_TO_NGTCP2 = "/Users/kevin/Documents/UHasselt/Masterjaar2/Masterproef/ngtcp/ngtcp2"


class QuicRequestThread (threading.Thread):
   def __init__(self, server, resource, command):
      threading.Thread.__init__(self)
      self.server = server
      self.resource = resource
      self.command = command

   def run_command(self, command, stdout=None, stderr=None):
       subprocess.call(command.split(), stdout=stdout, stderr=stderr)

   def run(self):
       self.run_command(self.command, open(os.devnull, 'w'), subprocess.STDOUT)

def get_run_test_client_command(server, resource):
    return LOCAL_PATH_TO_NGTCP2 + "/examples/client " + server + " 4433 -d ./request.txt"

def create_temporary_request_file(resource):
    f = open("./request.txt", "w+")
    f.write("GET /" + resource + "\n")
    f.flush()
    f.close()

def remove_temp_request_file():
    os.remove("./request.txt")

def start_tcpdump(server, resource, amount):
    command = "tcpdump -i any -s0 udp port 4433 -U -w /logs/" + \
        server + "-" + str(amount) + "-" + resource + ".pcap"
    return subprocess.Popen(command.split())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--server', help='Server name that is tested with this client script', required=True)
    parser.add_argument(
        '-a', '--amount', help='Amount of connections to open', required=True, default=1, type=int)
    parser.add_argument(
        '-r', '--resource', help='Resource that needs to be requested by the clients', required=True)

    args = parser.parse_args()

    run_client_command = get_run_test_client_command(
        args.server, args.resource)

    create_temporary_request_file(args.resource)
    tcpdump_process = start_tcpdump(args.server, args.resource, args.amount)
    try:
        client_pool = []
        for i in range(0, args.amount):
            request_thread = QuicRequestThread(args.server, args.resource, run_client_command)
            client_pool.append(request_thread)
        for request_thread in client_pool:
            request_thread.start()
        for request_thread in client_pool:
            request_thread.join()
    except KeyboardInterrupt:
        print("keyboard interrupt")
    except Exception as e:
        print(e)
        print("exception")
    print("cleaning up")
    tcpdump_process.send_signal(signal.SIGINT)
    remove_temp_request_file()


if __name__ == "__main__":
  main()
