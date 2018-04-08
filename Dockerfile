FROM python:3.6
MAINTAINER susnote

ADD . /susnote/
WORKDIR /susnote
RUN pip install -i 'http://pypi.douban.com/simple' --trusted-host pypi.douban.com -r requirements.txt
WORKDIR /susnote/app

EXPOSE 8000
