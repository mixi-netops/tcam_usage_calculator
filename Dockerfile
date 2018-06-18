FROM python:3.6.5-stretch
MAINTAINER hekki

RUN apt-get update
RUN apt-get install -y python3 python3-setuptools wget

RUN mv /etc/services /etc/services.origin
RUN wget https://raw.githubusercontent.com/freebsd/freebsd/master/etc/services -P /etc

WORKDIR /usr/src/tcap_usage_caluclator
COPY . .
RUN [ "python3", "setup.py", "install" ]
