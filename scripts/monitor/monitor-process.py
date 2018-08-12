import os
import sys
import psutil
import time
import argparse
import csv
from apscheduler.schedulers.blocking import BlockingScheduler

start_time = None

def monitor_process(name, proc, path, file):
    global start_time
    if not proc.is_running():
        exit(0)
    if start_time is None:
        start_time = time.time()
    stats_dict = {}
    with proc.oneshot():
        netio = psutil.net_io_counters()
        diskio = psutil.disk_io_counters()
        stats_dict["name"] = name
        stats_dict["memory"] = proc.memory_percent()
        stats_dict["cpu"] = proc.cpu_percent()
        stats_dict["network_io"] = {
            "sent": netio.bytes_sent,
            "recv": netio.bytes_recv
        }
        stats_dict["disk_io"] = {
            "read": diskio.read_bytes,
            "write": diskio.write_bytes
        }
    process_stats(name, path, file, stats_dict, round(time.time() - start_time, 2))


def process_stats(name, path, file, stats_dict, time):
    if not path.endswith('/'):
        path = path + "/"
    with open(path + file, 'a+') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        csv_writer.writerow([
            str(time), stats_dict.get("name"), 
            stats_dict.get("memory"),stats_dict.get("cpu"),
            stats_dict.get("network_io").get('sent'),
            stats_dict.get("network_io").get('recv'),
            stats_dict.get("disk_io").get('read'),
            stats_dict.get("disk_io").get('write')
        ])
    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--process_id', help='Process id to monitor', required=True)
    parser.add_argument('-n', '--name', help='Name of the server where the script is running on', required=True)
    parser.add_argument('-f', '--file', help="Filename of the csv file", required=True)
    parser.add_argument('-p', '--path', help="Path to write the csv file to", required=True)
    args = parser.parse_args()

    proc = psutil.Process(int(args.process_id))

    sched = BlockingScheduler()
    sched.add_job(monitor_process, 'interval', [args.name, proc, args.path, args.file], seconds=0.5)
    sched.start()

if __name__ == "__main__":
  main()
