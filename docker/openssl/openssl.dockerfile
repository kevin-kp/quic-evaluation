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
    tcpdump             \
    && apt-get autoremove     \
    && apt-get clean

# clone openssl
RUN git clone https://github.com/openssl/openssl /openssl

WORKDIR /openssl

# Go to draft version 28 available
RUN git checkout 58094ab60ff51918a248dc6bd977d48f981fe2c1

# build and install openssl
RUN ./config --prefix=$PWD/build && make && make install
