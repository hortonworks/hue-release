# Welcome to Hue (http://gethue.com) Dockerfile

FROM ubuntu:18.04
LABEL description="Hue SQL Assistant - gethue.com"

# TODO: run as hue from the start to avoid the long chmod

RUN export PYTHON_VER=python3.6

RUN apt-get update -y && apt-get install -y \
  python3-pip \
  libkrb5-dev  \
  libsasl2-modules-gssapi-mit \
  libsasl2-dev \
  libkrb5-dev \
  libxml2-dev \
  libxslt-dev \
  libmysqlclient-dev \
  libldap2-dev \
  libsnappy-dev \
  python3.6-venv \
  rsync \
  curl \
  sudo \
  git

#libmariadb-dev-compat  # python3.6-dev #libssl-dev

RUN pip3 install --upgrade setuptools
RUN pip3 install virtualenv

# Need recent version for Ubuntu
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo bash - \
  && apt-get install -y nodejs

RUN addgroup hue && useradd -r -u 1001 -g hue hue

ADD . /hue
WORKDIR /hue

RUN chown -R hue /hue

RUN mkdir /hue/build && chown -R hue /hue/build && mkdir /usr/share/hue && chown -R hue /usr/share/hue

# Not doing a `make prod`, so manually getting production ini
RUN rm desktop/conf/*
COPY desktop/conf.dist desktop/conf

#USER hue

#RUN python3.6 -m venv python_env

#SHELL ["/bin/bash", "-c"]
#RUN source python_env/bin/activate

RUN rm -r desktop/core/ext-py
# RUN pip3 install -r desktop/core/requirements.txt


RUN PREFIX=/usr/share PYTHON_VER=python3.6 make install
RUN chown -R hue /usr/share/hue
#RUN useradd -ms /bin/bash hue && chown -R hue /usr/share/hue


# Only keep install dir
# Note: get more minimal image by pulling install dir in a stage 2 image
WORKDIR /usr/share/hue
RUN rm -rf /hue \
  && rm -rf node_modules

# Install DB connectors
# To move to requirements_connectors.txt
RUN ./build/env/bin/pip install \
  psycopg2-binary \
  redis==2.10.6 \
  django_redis \
  flower \
  git+https://github.com/gethue/PyHive #pyhive \
  gevent \
  threadloop  # Needed for Jaeger \
  thrift-sasl==0.2.1


COPY tools/docker/hue/conf desktop/conf
COPY tools/docker/hue/startup.sh .

EXPOSE 8888
CMD ["./startup.sh"]
