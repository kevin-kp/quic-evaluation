FROM openssl:tls13
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
    cmake \
    && apt-get autoremove \
    && apt-get clean

WORKDIR /

# Clone quicly
RUN git clone -b experiment-branch https://github.com/kevin-kp/quicly.git /quicly

WORKDIR /quicly

RUN git submodule update --init --recursive
RUN PKG_CONFIG_PATH=/openssl/lib/pkgconfig cmake .
RUN make
RUN make check

# copy keys for the server
COPY ./docker/keys /keys/
# copy scripts
COPY ./scripts /scripts/
# copy www folder
COPY ./www/* /quicly/assets/

# install python dependencies for the scripts that are going to be used
RUN pip install --upgrade pip
RUN pip install apscheduler psutil

EXPOSE 4433