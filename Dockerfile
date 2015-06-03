# builds deployment environment and then push changes
FROM ubuntu:14.04
RUN apt-get update -qy
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-client \
                                                      python-mysqldb \
                                                      python-pil \
                                                      python-setuptools \
                                                      python-dev \
                                                      build-essential \
                                                      curl \
                                                      unzip \
                                                      rubygems1.9.1 \
                                                      git \
                                                      jq
RUN easy_install pip
RUN gem install sass --version '3.3.4'
RUN cd /opt; curl -O -s https://storage.googleapis.com/appengine-sdks/deprecated/1918/google_appengine_1.9.18.zip && \
    unzip -qq google_appengine_1.9.18.zip && rm google_appengine_1.9.18.zip
ENV PATH /opt/google_appengine:$PATH
ADD . /opt/codeforlife-deploy/
ENV TMPDIR /pip
RUN mkdir -p $TMPDIR
RUN /bin/echo -e "Host *\n  StrictHostKeyChecking no" | tee /etc/ssh/ssh_config
CMD ["/opt/codeforlife-deploy/deploy.sh"]
