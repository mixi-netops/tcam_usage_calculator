FROM python:3.6.5-stretch
MAINTAINER hekki

RUN apt-get update
RUN apt-get install -y python3 python3-setuptools wget

WORKDIR /usr/src/tcap_usage_caluclator
COPY . .
RUN [ "python3", "setup.py", "install" ]
