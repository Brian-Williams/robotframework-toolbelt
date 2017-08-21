FROM ubuntu:16.04
MAINTAINER Brian Williams

COPY / /repo
RUN apt-get update && \
    apt-get install -y \
      python-pip  && \
    pip install -e /repo

CMD python -i /repo/.docker/import.py
