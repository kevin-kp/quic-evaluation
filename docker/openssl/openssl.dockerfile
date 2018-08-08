FROM ubuntu:16.04
ENV TERM dumb

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

# clone openssl
RUN git clone --depth 1 https://github.com/openssl/openssl /openssl

WORKDIR /openssl

# build and install openssl
RUN ./config --prefix=$PWD/build && make && make install
