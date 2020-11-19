FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

RUN apt-get update && apt-get install -y python3 python3-dev vim python3-pip

RUN mkdir /code

COPY setup.py /code
COPY requirements.txt /code/requirements.txt
COPY *.py /code/
COPY scale /code
COPY *.sh /code/
RUN cd /code && python3 setup.py install
