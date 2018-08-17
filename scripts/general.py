import subprocess
import time

QUIC_RESULTS_DIRECTORY = "/Users/kevin/Documents/quic-results"
test_datetime_str = time.strftime("%Y%m%d-%H%M%S")

def update_start_time():
    global test_datetime_str
    test_datetime_str = time.strftime("%Y%m%d-%H%M%S")

def run_subprocess_command(command):
    process = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    #if error is not None:
    #    print("error in command: " + command)
    #    print("error: " + error)
    #    exit(-1)
    return output.rstrip()


def run_call_command(command):
    subprocess.call(command.split(), stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)


def get_host_directory(test_name, name, is_server):
    global test_datetime_str
    subdir = "server" if is_server else "client"
    host_dir = QUIC_RESULTS_DIRECTORY + "/" + test_name + \
        "/" + test_datetime_str + "/" + subdir + "/" + name
    run_subprocess_command("mkdir -p " + host_dir)
    run_subprocess_command("chmod -R 777 " + host_dir)
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


def create_server_container(test_name, image, name=None, entrypoint=None):
    print("creating server container")
    if name is None:
        name = image
    host_dir = get_host_directory(test_name, name, True)
    command = "docker run --rm --privileged --name " + name + \
        " -d -i -p 4433:4433/udp -v " + host_dir + ":/logs:Z " + image + ":latest"
    if entrypoint is not None:
        command += " --entrypoint " + entrypoint
    print("server run command: " + command)
    output = run_subprocess_command(command)
    print("created server container with id: " + output)
    return output


def create_client_container(test_name, image, server_name, name=None, entrypoint=None):
    print("creating client container")
    if name is None:
        name = image
    host_dir = get_host_directory(test_name, name, False)
    command = "docker run --rm --privileged --name " + name + " --link " + \
        server_name + " -d -i -v " + host_dir + ":/logs:Z " + image + ":latest"
    print("client run command: " + command)
    if entrypoint is not None:
        command += " --entrypoint " + entrypoint
    output = run_subprocess_command(command)
    print("created client container with id: " + output)
    return output


def restart_test_client(test_name, client, client_name, client_container_id, server_name):
    print("restarting client")
    if client_container_id is not None:
        remove_container(client_container_id)
    client_container_id = create_client_container(test_name, client, server_name, client_name)
    return client_container_id
