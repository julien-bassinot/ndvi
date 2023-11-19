FROM orfeotoolbox/otb:latest

RUN apt-get update && \
    apt-get --assume-yes install python3-pip

COPY requirements.txt /
RUN pip install -r requirements.txt

