FROM node:qtls
ENV TERM dumb

# to generate new self-signed cert for testing 
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout keys/temp.key -out keys/temp.crt

RUN apt-get install -y \
    tcpdump \
    && apt-get autoremove \
    && apt-get clean

# Clone quicker
RUN git clone -b draft-12+PR#1389 https://github.com/kevin-kp/quicker.git /server

# Install typescript which is necesarry for quicker
RUN npm install typescript -g

WORKDIR /server

# Install dependencies quicker
RUN npm install

# Build quicker 
#RUN tsc -p ./

# copy keys for the server
COPY ./docker/keys /keys/
# copy scripts
COPY ./scripts /scripts/
# copy www folder
COPY ./www /www/

# install python dependencies for the scripts that are going to be used
RUN pip install --upgrade pip
RUN pip install apscheduler psutil

EXPOSE 4433/UDP
#CMD [ "node", "/server/out/main.js" ]
#CMD [ "node", "/server/out/main.js", "127.0.0.1", "4433", "./keys/selfsigned_default.key", "./keys/selfsigned_default.crt" ]
#ENTRYPOINT [ "sh", "/server/scripts/run-scripts/server/build_quicker_and_run.sh", "0.0.0.0", "4433", "/keys/domain.key", "/keys/domain.crt"]
