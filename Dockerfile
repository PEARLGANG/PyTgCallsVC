FROM python:3.9

RUN apt update && apt upgrade -y
RUN apt install git curl python3-pip ffmpeg -y
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm
RUN pip3 install -U pip
RUN mkdir /py-tgcalls/
WORKDIR /py-tgcalls/
COPY . /py-tgcalls/
RUN pip3 install -U -r requirements.txt
RUN pip3 install py-tgcalls -U
CMD python3 vcbot
