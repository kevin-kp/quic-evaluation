FROM ubuntu:16.04

# install necessary packages
RUN rm -rf /var/lib/apt/lists/*  \
    && apt-get clean \
    && apt-get update --fix-missing         \
    && apt-get upgrade -y     \
    && apt-get install -y     \
    build-essential     \
    gcc                 \
    make                 \
    python-pip             \
    python2.7             \
    nasm                 \
    git                 \
    && apt-get autoremove     \
    && apt-get clean

# Copy github file
COPY ./docker/quicker/github_key_file /keyfiles/github_key_file

# Clone custom nodejs
RUN   chmod 600 /keyfiles/github_key_file && \
    echo "IdentityFile /keyfiles/github_key_file\n" >> /etc/ssh/ssh_config && \
    echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config && \
    git clone -b add_quicker_support-tls-d28 git@github.com:kevin-kp/node.git /node

WORKDIR /node/deps/openssl/config

RUN make

RUN chmod 777 /node/configure && cd /node && ./configure --openssl-no-asm

RUN cd /node && make -j2 && make install


CMD ["/bin/bash"]