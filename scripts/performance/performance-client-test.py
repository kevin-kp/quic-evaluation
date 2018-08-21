import subprocess
import argparse
import signal
import os
import threading

LOCAL_PATH_TO_NGTCP2 = "/Users/kevin/Documents/UHasselt/Masterjaar2/Masterproef/ngtcp/ngtcp2"
LOG_DIRECTORY = "/Users/kevin/Documents/quic-results/performance"
DEV_NULL = open(os.devnull, 'w')


class QuicRequestThread (threading.Thread):
   def __init__(self, thread_id, server, resource, command):
      threading.Thread.__init__(self)
      self.thread_id = thread_id
      self.server = server
      self.resource = resource
      self.command = command
      self.thread_process = None

   def stop_thread(self):
       if self.thread_process is not None and self.check_pid(self.thread_process.pid):
           self.thread_process.terminate()
           self.thread_process.wait()

   def run_command(self, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
       return subprocess.Popen(command.split(), stdout=stdout, stderr=stderr)

   def run(self):
       with open("/Users/kevin/Documents/quic-results/performance_measures/damn_client_logs/" + self.server + "-" + str(self.thread_id) + ".txt","w+") as out:
           self.thread_process = self.run_command(
               self.command, out, out)
           self.thread_process.wait()

    # source check_pid: https://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python
   def check_pid(self, pid):        
       """ Check For the existence of a unix pid. """
       try:
           # does not do anything when if pid is running
           os.kill(pid, 0)
       except OSError:
           return False
       else:
           return True


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
    command = "tcpdump -i any -s0 udp port 4433 -U -w " + LOG_DIRECTORY + "/" + \
        server + "-" + str(amount) + "-" + resource + ".pcap"
    return subprocess.Popen(command.split())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--server', help='Server IP that is tested with this client script', required=True)
    parser.add_argument(
        '-n', '--name', help='Server name that is tested with this client script', required=True)
    parser.add_argument(
        '-a', '--amount', help='Amount of connections to open', required=True, default=1, type=int)
    parser.add_argument(
        '-r', '--resource', help='Resource that needs to be requested by the clients', required=True)

    args = parser.parse_args()

    run_client_command = get_run_test_client_command(
        args.server, args.resource)

    create_temporary_request_file(args.resource)
    tcpdump_process = start_tcpdump(args.name, args.resource, args.amount)
    client_pool = []
    try:
        for i in range(0, args.amount):
            request_thread = QuicRequestThread(i,
                args.server, args.resource, run_client_command)
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
    for request_thread in client_pool:
        request_thread.stop_thread()
    tcpdump_process.send_signal(signal.SIGINT)
    remove_temp_request_file()


if __name__ == "__main__":
  main()
