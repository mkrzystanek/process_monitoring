FROM ubuntu:latest

SHELL ["/bin/bash", "-c"]

RUN apt-get update
RUN yes | apt-get install python3
RUN yes | apt-get install python3-pip
RUN yes | apt-get install python3.10-venv

ADD ./ ./MemoryLeak
WORKDIR /MemoryLeak

RUN python3 -m venv ./venv
RUN source ./venv/bin/activate
RUN python3 -m pip install -r ./requirements.txt