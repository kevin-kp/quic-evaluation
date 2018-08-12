from openssl:tls13
ENV TERM dumb

# Install packages needed for ngtcp2
RUN rm -rf /var/lib/apt/lists/*  \
    && apt-get clean \
    && apt-get update --fix-missing         \
    && apt-get upgrade -y     \
    && apt-get install -y     \
    autoconf \ 
    automake \ 
    autotools-dev \ 
    libtool \ 
    libev-dev \
    pkg-config \
    cmake           

# Clone picotls
RUN git clone https://github.com/h2o/picotls /picotls

# Clone picoquic
RUN git clone https://github.com/private-octopus/picoquic /picoquic

WORKDIR /picoquic

RUN git checkout 3aa4e448ef4e9da257cd4b222a36ec8010f9dfa7

# Build picotls
WORKDIR /picotls

RUN git checkout c07a6ac08586d2fd177e7871c6ee879e4ac11603

RUN git submodule init && \
    git submodule update && \
    PKG_CONFIG_PATH=/openssl/build/lib/pkgconfig cmake . && \
    make

# Build picoquic
WORKDIR /picoquic

RUN PKG_CONFIG_PATH=/openssl/build/lib/pkgconfig cmake . && \
    make

# copy keys for the server
COPY ./docker/keys /keys/
# copy scripts
COPY ./scripts /scripts/
# copy www folder
COPY ./www /www/

# install python dependencies for the scripts that are going to be used
RUN pip install apscheduler, psutil

EXPOSE 4433/UDP
#./picoquicdemo -c /keys/domain.crt -k /keys/domain.key -p 4433
#ENTRYPOINT ["/picoquic/picoquicdemo", "-c", "/keys/domain.crt", "-k", "/keys/domain.key", "-p", "4433"]