FROM ubuntu:16.04
MAINTAINER Yorling "i@yorling.com"

ADD . /opt/app
COPY sources.list /etc/apt/sources.list
COPY supervisor-app.conf /etc/supervisor/conf.d/
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-setuptools \
    nginx \
    supervisor
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
WORKDIR /opt/app
RUN pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple/
COPY manager.conf /etc/nginx/sites-enabled/default
RUN python3 manager/manage.py collectstatic --noinput && \
    python3 manager/manage.py makemigrations --noinput && \
    python3 manager/manage.py migrate --noinput

EXPOSE 80

CMD ["supervisord", "-n"]

