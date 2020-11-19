FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

RUN apt-get update && apt-get install -y python3 python3-dev vim python3-pip

RUN apt-get install -y zlib1g zlib1g-dev
RUN apt-get install -y sudo

RUN apt-get install -y llvm
RUN useradd -ms /bin/bash ubuntu && adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
user ubuntu
workdir /home/ubuntu


COPY setup.py /home/ubuntu
COPY requirements.txt /home/ubuntu/requirements.txt
COPY *.py /home/ubuntu/
COPY scale /home/ubuntu/scale
COPY *.sh /home/ubuntu/
COPY requirements-cuda.txt /home/ubuntu
ENV LANG="C.UTF-8"
RUN cd /home/ubuntu && sudo python3 setup.py install && sudo pip3 install -r requirements-cuda.txt
