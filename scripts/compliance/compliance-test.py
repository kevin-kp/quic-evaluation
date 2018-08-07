import subprocess

def run_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()

def remove_container(container_id):
    # Remove container if it exists
    output, error = run_command("docker ps -aq")
    if container_id in output:
        # stop removes container because they are all started with the --rm parameter
        run_command("docker stop " + container_id)

def remove_containers():
    # check if there are containers open
    output, error = run_command("docker ps -aq")
    if output != "":
        # stop removes container because they are all started with the --rm parameter
        run_command("docker stop $(docker ps -aq)")

def create_container(image, name = None):
    if name is None:
        name = image
    command = "docker run --rm --privileged --name " + name + " -d -i -p 4433:4433/udp " + image + ":latest"
    output, error = run_command(command)
    return output

def restart_test_client(client_container_id = None):
    if client_container_id is not None:
        remove_container(client_container_id)
    client_container_id = create_container("quicker", "client-quicker")
    return client_container_id

def run_test_client(client_container_id):
    if client_container_id is None:
        print("cannot run test client, no container")
        exit(-1)
    command = "docker exec -i " + client_container_id + " python ‘/scripts/compliance/compliance-client-test.py’"
    output, error = run_command(command)
    return output

def main():
    implementations = ["ats","ngtcp2","picoquic","quicker","quant"]
    remove_containers()
    client_container_id = None
    for implementation in implementations:
        container_id = create_container(implementation)
        client_container_id = restart_test_client(client_container_id=client_container_id)
        run_test_client(client_container_id)
        remove_container(container_id)


if __name__== "__main__":
  main()