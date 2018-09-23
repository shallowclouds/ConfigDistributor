FROM ubuntu:16.04
MAINTAINER Yorling "i@yorling.com"

ADD . /opt/config_distributor
COPY sources.list /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-setuptools \
    nginx \
    supervisor
WORKDIR /opt/config_distributor
RUN pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple/
RUN cp manager.conf /etc/nginx/sites-enabled/
RUN python3 manage.py collectstatics
RUN service nginx start
EXPOSE 80
CMD ["uwsgi", "--ini", "uwsgi.ini"]
