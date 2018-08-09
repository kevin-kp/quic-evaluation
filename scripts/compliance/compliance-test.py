import subprocess
import time

QUIC_RESULTS_DIRECTORY = "/Users/kevin/Documents/quic-results"

def run_subprocess_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    #if error is not None:
    #    print("error occured when running command: " + command)
    #    exit(-1)
    return output.rstrip()

def run_call_command(command):
    subprocess.call(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_host_directory(name, is_server):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    subdir = "server" if is_server else "client"
    host_dir = QUIC_RESULTS_DIRECTORY + "/" + name + "/" + subdir + "/" + timestr
    run_subprocess_command("mkdir -p " + host_dir)
    run_subprocess_command("sudo chmod -R 777 " + QUIC_RESULTS_DIRECTORY)
    return host_dir

def get_short_container_id(container_id):
    return run_subprocess_command("docker inspect --format={{.Config.Hostname}} " + container_id)

def remove_container(container_id):
    # Remove container if it exists
    output = run_subprocess_command("docker ps -aq")
    short_container_id = get_short_container_id(container_id)
    if short_container_id in output:
        # stop removes container because tchey are all started with the --rm parameter
        print("stopping container " + container_id)
        run_subprocess_command("docker stop " + container_id)

def remove_containers():
    # check if there are containers open
    output = run_subprocess_command("docker ps -aq")
    for container_id in output.split():
        remove_container(container_id)

def create_server_container(image, name = None, entrypoint = None):
    print("creating server container")
    if name is None:
        name = image
    host_dir = get_host_directory(name, True)
    command = "docker run --rm --privileged --name " + name + " -d -i -p 4433:4433/udp -v " + host_dir + ":/logs:Z " + image + ":latest"
    if entrypoint is not None:
        command += " --entrypoint " + entrypoint
    output = run_subprocess_command(command)
    print("created server container with id: " + output)
    return output

def create_client_container(image, server_name, name = None, entrypoint = None):
    print("creating client container")
    if name is None:
        name = image
    host_dir = get_host_directory(name, False)
    command = "docker run --rm --privileged --name " + name + " --link " + server_name + " -d -i -v " + host_dir + ":/logs:Z " + image + ":latest"
    if entrypoint is not None:
        command += " --entrypoint " + entrypoint
    output = run_subprocess_command(command)
    print("created client container with id: " + output)
    return output

def restart_test_client(client_container_id, server_name):
    print("restarting client")
    if client_container_id is not None:
        remove_container(client_container_id)
    client_container_id = create_client_container("quicker", server_name, "client-quicker", "/bin/bash")
    return client_container_id

def run_test_client(client_container_id, server_name):
    print("starting test client to test " + server_name)
    if client_container_id is None:
        print("cannot run test client, no container")
        exit(-1)
    command = "docker exec -i " + client_container_id + " python /scripts/compliance/compliance-client-test.py " + server_name
    run_call_command(command)

def main():
    implementations = ["ngtcp2","quicker","quant"]
    remove_containers()
    client_container_id = None
    for implementation in implementations:
        container_id = create_server_container(implementation)
        client_container_id = restart_test_client(client_container_id, implementation)
        run_test_client(client_container_id, implementation)
        remove_container(container_id)
    print("compliance test done")

if __name__== "__main__":
  main()