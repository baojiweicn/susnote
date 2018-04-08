FROM python:3.6
MAINTAINER susnote

ADD . /susnote/
WORKDIR /susnote
RUN pip install -i 'http://pypi.douban.com/simple' --trusted-host pypi.douban.com -r requirements.txt
WORKDIR /susnote/app

EXPOSE 8000

FROM redis
COPY redis.conf /usr/local/etc/redis/redis.conf
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
