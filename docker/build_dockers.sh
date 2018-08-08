
# Build openssl docker
docker build -t openssl:tls13 -f ./openssl/openssl.dockerfile ./../

# Build ats docker
#docker build -t ats:latest -f ./ats/ats.dockerfile ./../


# Build ngtcp2 docker
docker build -t ngtcp2:latest -f ./ngtcp2/ngtcp2.dockerfile ./../


# Build picoquic docker
#docker build -t picoquic:latest -f ./picoquic/picoquic.dockerfile ./../


# Build quant docker
docker build -t quant:latest -f ./quant/quant.dockerfile ./../


# Build quicker dockers
docker build -t node:qtls -f ./quicker/node.dockerfile ./../
docker build -t quicker:latest -f ./quicker/quicker.dockerfile ./../
