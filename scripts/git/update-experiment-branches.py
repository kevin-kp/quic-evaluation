import subprocess

###
# Merges draft-12+PR#1389 in experiment branches and only succeeds when there are no merge conflicts ...
###

def run_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()

experiment_branches = [
        # Quicker sents a badly formed frame
        "exp-badly-formed-frame",
        # Quicker sents data after fin bit was set on a stream
        "exp-data-after-fin",
        # Quicker sents all packets duplicate
        "exp-duplicate-packets",
        # Quicker sets its max_stream_data very low
        "exp-flow-control",
        # Quicker sents a lot of handshake packets in a single UDP datagram
        "exp-many-quic-in-udp",
        # Quicker sents packets reversed from the buffer
        "exp-out-of-order",
        # Quicker sents random bytes
        "exp-random-bytes",
        # Quicker requests a resource with HTTP on a Server unidirectional stream
        "exp-request-wrong-stream",
        # Quicker starts with a handshake packet instead of initial packet
        "exp-start-hs-frame",
        # Quicker sents a stop sending frame on a client unidirectional stream
        "exp-stop-sending-cli-uni",
    ]

for branch in experiment_branches:
    command = "git checkout " + branch
    run_command(command)
    run_command("git merge draft-12+PR#1389")