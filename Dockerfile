FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code



RUN apt-get update
RUN apt-get -y install python3-dev python-dev libzmq3-dev 
RUN apt-get -y install npm nodejs-legacy
RUN npm install -g configurable-http-proxy
RUN apt-get -y install libfreetype6-dev
RUN apt-get -y install python3-matplotlib
RUN apt-get -y install pciutils
ADD requirements.txt /code/
RUN pip install -r requirements.txt

RUN useradd -ms /bin/bash myuser
RUN echo "myuser:Docker!" | chpasswd
USER myuser
WORKDIR /home/myuser
RUN mkdir /home/myuser/DTN_monitor
WORKDIR /home/myuser/DTN_monitor
ADD . /home/myuser/DTN_monitor

USER root
WORKDIR /home/myuser/DTN_monitor
CMD ["jupyterhub"]