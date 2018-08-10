FROM ubuntu:16.04
ENV TERM dumb

# install necessary packages
RUN rm -rf /var/lib/apt/lists/*  \
    && apt-get clean \
    && apt-get update --fix-missing         \
    && apt-get upgrade -y     \
    && apt-get install -y     \
    build-essential \
    gcc \
    make \
    python-pip \
    python2.7 \
    nasm \
    git \
    libev-dev \
    libssl-dev \
    libhttp-parser-dev \
    libbsd-dev \
    doxygen \
    graphviz \
    mercurial \
    pkg-config \
    tcpdump   \
    wget \
    && apt-get autoremove \
    && apt-get clean

WORKDIR /
RUN wget https://cmake.org/files/v3.12/cmake-3.12.0.tar.gz
RUN tar -xvzf cmake-3.12.0.tar.gz
WORKDIR /cmake-3.12.0
RUN ./configure && make && make install

# copy keys for the server
COPY ./docker/keys /keys/
# copy scripts
COPY ./scripts /scripts/

# Clone quant
RUN git clone --depth 1 -b 12 https://github.com/NTAP/quant.git /quant

WORKDIR /quant

# Create folders for debug and build debug
RUN mkdir Debug && mkdir ./Debug/external && mkdir ./Debug/external/lib

WORKDIR ./Debug

RUN cmake .. && make

WORKDIR ../

# Create folders for release and build release
RUN mkdir Release && mkdir ./Release/external && mkdir ./Release/external/lib

WORKDIR ./Release

RUN cmake -DCMAKE_BUILD_TYPE=Release .. && make

EXPOSE 4433/UDP

#ENTRYPOINT ["/quant/bin/server", "-d", "/", "-i", "eth0", "-p", "4433:4433/udp", "-k", "/keys/domain.key", "-c", "/keys/domain.crt"]