import subprocess

experiment_branches = [
    "draft-12+PR#1389", # Check the working ,
    "exp-badly-formed-frame",
    "exp-data-after-fin",
    "exp-duplicate-packets",
    "exp-flow-control",
    "exp-many-quic-in-udp",
    "exp-out-of-order",
    "exp-random-bytes",
    "exp-request-wrong-stream",
    "exp-start-hs-frame",
    "exp-stop-sending-cli-uni",
]

run_quicker_client = "sh ./scripts/run-scripts/client/build_quicker_and_run.sh 127.0.0.1 4433"


# TODO: save output from quicker to a file instead of printing this
for branch in experiment_branches:
    command = "git checkout " + branch
    subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process = subprocess.Popen(run_quicker_client.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)
