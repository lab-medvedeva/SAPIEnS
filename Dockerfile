FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

RUN apt-get install -y zlib1g zlib1g-dev libxml2-dev libssl-dev
RUN apt-get install -y sudo

RUN apt-get install -y llvm
RUN useradd -ms /bin/bash ubuntu && adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
user ubuntu
workdir /home/ubuntu


COPY setup.py /home/ubuntu
COPY requirements.txt /home/ubuntu/requirements.txt
COPY . /home/ubuntu
COPY ./imputation/SCALE /home/ubuntu/SCALE
COPY requirements-cuda.txt /home/ubuntu
ENV LANG="C.UTF-8"
