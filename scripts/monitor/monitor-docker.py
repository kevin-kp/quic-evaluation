import subprocess
import json
import csv
import argparse
import time

def get_docker_stats_format():
    return ' \
        { \
            \"id\":\"{{ .ID }}\", \
            \"name\":\"{{ .Name }}\", \
            \"memory\": \
            { \
                \"raw\":\"{{ .MemUsage }}\", \
                \"percent\":\"{{ .MemPerc }}\" \
            },\
            \"cpu\":\"{{ .CPUPerc }}\", \
            \"network\": \"{{ .NetIO }}\" \
        }'

def process_docker_stats(stats, path, file):
    print("stats: " + repr(stats))
    print("out: " + str(json.loads(stats)))

def log_docker_stats(container_id, path, file):
    start_time = None
    splitted_command = "docker stats --format".split()
    splitted_command.append(get_docker_stats_format())
    splitted_command.append(container_id)
    proc = subprocess.Popen(splitted_command, stdout=subprocess.PIPE)
    while True:
        output = proc.stdout.readline()
        if start_time is None:
            start_time = time.time()
        print("\time: " + str(round(time.time() - start_time, 2)))
        if output == '' and proc.poll() is not None:
            break
        if output:
            process_docker_stats(output.rstrip().replace('\x1b[2J\x1b[H',''), path, file)
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--container', help='Container id to monitor', required=True)
    parser.add_argument('-f', '--file', help="Filename of the csv file", required=True)
    parser.add_argument('-p', '--path', help="Path to write the csv file to", required=True)

    args = parser.parse_args()
    log_docker_stats(args.container, args.path, args.file)

if __name__ == "__main__":
  main()
