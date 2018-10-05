FROM ubuntu:16.04
LABEL maintainer = "i@yorling.com"
LABEL author = "Yorling"
LABEL version = "1.0"
LABEL project.name = "ConfigDistributor" \
      project.url = "https://github.com/shallowclouds/ConfigDistributor" \
      project.docs = "https://github.com/shallowclouds/ConfigDistributor/blob/develop/README.md"

ADD . /opt/app
COPY sources.list /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-setuptools \
    nginx \
    redis-server \
    supervisor && \
    echo "daemon off;" >> /etc/nginx/nginx.conf && \
    echo "daemon off;" >> /etc/redis/redis.conf
COPY supervisor-app.conf /etc/supervisor/conf.d/
WORKDIR /opt/app
RUN pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple/
COPY manager.conf /etc/nginx/sites-enabled/default
RUN python3 manager/manage.py collectstatic --noinput && \
    python3 manager/manage.py makemigrations --noinput && \
    python3 manager/manage.py migrate --noinput && \
    python3 manager/manage.py loaddata init_users

EXPOSE 80

CMD ["supervisord", "-n"]

