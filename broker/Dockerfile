FROM ubuntu:17.10
ENV LANG en_US.UTF-8
ENV PYTHONIOENCODING UTF-8
# Install.
RUN apt-get update && \
  apt-get -y upgrade

RUN apt-get update
RUN apt-get install -y supervisor # Installing supervisord
RUN apt-get install -y python2.7 software-properties-common python2.7-dev python-psycopg2 python-pip
RUN pip install pymongo
RUN pip install bs4
RUN pip install unidecode
RUN pip install paho-mqtt

#ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root
#RUN mkdir conf
ADD . /root

VOLUME ["/root/conf"]


# Define default command.
ENTRYPOINT ["python","/root/mqtt.py"]
#ENTRYPOINT ["/usr/bin/supervisord"]
