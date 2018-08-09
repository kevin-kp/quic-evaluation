#!/usr/local/bin/python3

import subprocess
import time
import docker

client = docker.from_env()

QUIC_RESULTS_DIRECTORY = "/Users/kevin/Documents/quic-results"

def run_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is not None:
        print("error occured when running command: " + command)
        exit(-1)
    return output.rstrip()

def get_host_directory(name, is_server):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    subdir = "server" if is_server else "client"
    host_dir = QUIC_RESULTS_DIRECTORY + "/" + name + "/" + subdir + "/" + timestr
    run_command("mkdir -p " + host_dir)
    run_command("sudo chmod -R 777 " + QUIC_RESULTS_DIRECTORY)
    return host_dir

def remove_container(container):
    container.stop()

def remove_containers():
    global client
    for container in client.containers.list():
        container.stop()

def create_server_container(image, name = None):
    global client
    print("creating server container")
    if name is None:
        name = image
    host_dir = get_host_directory(name, True)
    container = client.containers.run(image + ":latest", detach=True, privileged=True, ports={'4433/udp': 4433}, name=name, remove=True, volumes={host_dir: {'bind': '/logs', 'mode': 'rw'}})
    print("created server container with id: " + container.id)
    return container

def create_client_container(image, name = None, entrypoint = None):
    global client
    print("creating client container")
    if name is None:
        name = image
    host_dir = get_host_directory(name, False)
    container = client.containers.run(image + ":latest", entrypoint=entrypoint, detach=True, privileged=True, ports={'4433/udp': 4433}, name=name, remove=True, volumes={host_dir: {'bind': '/logs', 'mode': 'rw'}})
    print("created client container with id: " + container.id)
    return container

def restart_test_client(client_container = None):
    print("restarting client")
    if client_container is not None:
        remove_container(client_container)
    client_container = create_client_container("quicker", "client-quicker", "/bin/bash")
    return client_container

def run_test_client(client_container, server_name):
    print("starting test client to test " + server_name)
    if client_container is None:
        print("cannot run test client, no container")
        exit(-1)
    client_container.exec_run("python3 /scripts/compliance/compliance-client-test.py " + server_name)

def main():
    implementations = ["ngtcp2","quicker","quant"]
    remove_containers()
    client_container = None
    for implementation in implementations:
        server_container = create_server_container(implementation)
        client_container = restart_test_client(client_container)
        run_test_client(client_container, implementation)
        remove_container(server_container)


if __name__== "__main__":
  main()