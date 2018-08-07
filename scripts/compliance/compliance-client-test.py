import subprocess

# TODO: get to test implementation via command param for logfile

experiment_branches = [
    "draft-12+PR#1389", # Check if implementation works with a correct quicker;
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

run_quicker_client = "sh ./scripts/run-scripts/client/build_quicker_and_run.sh 127.0.0.1 4433"


# TODO: save output from quicker to a file instead of printing this
for branch in experiment_branches:
    command = "git checkout " + branch
    subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process = subprocess.Popen(run_quicker_client.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)
