
FROM python:3.8
RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3-pip -y
RUN apt-get install ffmpeg -y
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g npm@7.22.0
WORKDIR /app
COPY . /app
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -U -r requirements.txt
CMD python3.8 -m vcbot
