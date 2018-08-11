FROM openssl:tls13
ENV TERM dumb

RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:jonathonf/gcc-7.1

# Install packages needed for ats
RUN rm -rf /var/lib/apt/lists/*  \
    && apt-get clean \
    && apt-get update --fix-missing         \
    && apt-get upgrade -y     \
    && apt-get install -y     \
    gcc-7 \
    g++-7 \
    autoconf \
    automake \
    autotools-dev \ 
    libtool \
    pkg-config \
    libev-dev \ 
    libmodule-install-perl \
    libssl-dev \
    tcl-dev \
    libpcre3-dev \
    # libcap-dev: optional, highly recommended
    libcap-dev \    
    # libhwloc-dev: optional, highly recommended
    libhwloc-dev 

# clone ATS with quic
RUN git clone -b quic-12 https://github.com/apache/trafficserver /trafficserver

WORKDIR /trafficserver

# Build and install ats
RUN autoreconf -if && CC=gcc-7 CXX=g++-7 ./configure --prefix=$PWD/atsbuild --with-openssl=/openssl/build --enable-debug && make && make install


# copy keys for the server
COPY ./docker/keys /keys/
# copy scripts
COPY ./scripts /scripts/
# copy www folder
COPY ./www /www/

EXPOSE 4433/UDP

