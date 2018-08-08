import subprocess

###
# Merges draft-12+PR#1389 in experiment branches and only succeeds when there are no merge conflicts ...
###

def run_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()

experiment_branches = [
    "exp-badly-formed-frame", # Quicker sents a badly formed frame
    "exp-data-after-fin", # Quicker sents data after fin bit was set on a stream
    "exp-duplicate-packets", # Quicker sents all packets duplicate
    "exp-flow-control", # Quicker sets its max_stream_data very low
    "exp-many-quic-in-udp", # Quicker sents a lot of handshake packets in a single UDP datagram
    "exp-out-of-order", # Quicker sents packets reversed from the buffer
    "exp-random-bytes", # Quicker sents random bytes
    "exp-request-wrong-stream", # Quicker requests a resource with HTTP on a Server unidirectional stream
    "exp-start-hs-frame", # Quicker starts with a handshake packet instead of initial packet
    "exp-stop-sending-cli-uni", # Quicker sents a stop sending frame on a client unidirectional stream
]

for branch in experiment_branches:
    command = "git checkout " + branch
    run_command(command)
    run_command("git merge draft-12+PR#1389")