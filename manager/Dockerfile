FROM dockerfiles/django-uwsgi-nginx
MAINTAINER Yorling "i@yorling.com"

RUN apt-get update -y
RUN apt-get install -y python3 python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["service nginx start"]
EXPOSE 80
