FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

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
COPY ./imputation/SCALE /home/ubuntu/SCALE
COPY requirements-cuda.txt /home/ubuntu
ENV LANG="C.UTF-8"
RUN cd /home/ubuntu/SCALE && sudo python3 setup.py install && sudo pip3 install -r requirements-cuda.txt
