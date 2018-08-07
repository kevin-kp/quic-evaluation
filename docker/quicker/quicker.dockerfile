FROM node:qtls

# to generate new self-signed cert for testing 
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout keys/temp.key -out keys/temp.crt

# Clone quicker
RUN git clone --depth 1 -b draft-12+PR#1389 https://github.com/rmarx/quicker.git /server

# Install typescript which is necesarry for quicker
RUN npm install typescript -g

WORKDIR /server

# copy keys for the server
COPY ./docker/keys /keys/
# copy scripts
COPY ./scripts /scripts/

# Install dependencies quicker
RUN npm install

# Build quicker 
#RUN tsc -p ./

EXPOSE 4433/UDP
#CMD [ "node", "/server/out/main.js" ]
#CMD [ "node", "/server/out/main.js", "127.0.0.1", "4433", "./keys/selfsigned_default.key", "./keys/selfsigned_default.crt" ]
CMD [ "sh", "/server/scripts/run-scripts/server/build_quicker_and_run.sh", "0.0.0.0", "4433", "/keys/domain.key", "/keys/domain.crt" ]
