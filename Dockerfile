FROM python:3
ENV PYTHONUNBUFFERED 1
RUN useradd -ms /bin/bash myuser
RUN echo "myuser:Docker!" | chpasswd

RUN mkdir /home/myuser/code
WORKDIR /code



RUN apt-get update
RUN apt-get -y install python3-dev python-dev libzmq3-dev 
RUN apt-get -y install npm nodejs-legacy
RUN npm install -g configurable-http-proxy
RUN apt-get -y install libfreetype6-dev
RUN apt-get -y install python3-matplotlib
RUN apt-get -y install pciutils
ADD requirements.txt WORKDIR /home/myuser/code
ADD . /home/myuser/code
RUN pip install -r requirements.txt

USER myuser
WORKDIR /home/myuser

USER root
WORKDIR /home/myuser/code/
CMD ["jupyterhub"]