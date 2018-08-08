# OS used
FROM openssl:tls13
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
    pkg-config 

# copy keys for the server
COPY ./docker/keys /keys/
# copy scripts
COPY ./scripts /scripts/

# Clone ngtcp2
RUN git clone https://github.com/ngtcp2/ngtcp2 /ngtcp2

WORKDIR /ngtcp2

# Fetch ngtcp2 when it implemented draft 12
RUN git checkout 769e8e5cfe45c1681a31aab32c22eb096d05afe0


# Build ngtcp2
RUN autoreconf -i && \
    ./configure PKG_CONFIG_PATH=/openssl/build/lib/pkgconfig LDFLAGS="-Wl,-rpath,/openssl/build/lib" && \
    make -j$(nproc) check

EXPOSE 4433/UDP
#CMD [ "node", "/server/out/main.js" ]
#CMD [ "node", "/server/out/main.js", "127.0.0.1", "4433", "./keys/selfsigned_default.key", "./keys/selfsigned_default.crt" ]
ENTRYPOINT [ "/ngtcp2/examples/server", "0.0.0.0", "4433", "/keys/domain.key", "/keys/domain.crt", ">>", "/logs/log.txt" ]