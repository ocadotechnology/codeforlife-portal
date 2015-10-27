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
RUN cd /opt; curl -O -s https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.27.zip && \
    unzip -qq google_appengine_1.9.27.zip && rm google_appengine_1.9.27.zip
ENV PATH /opt/google_appengine:$PATH
RUN /bin/echo -e "Host *\n  StrictHostKeyChecking no" | tee /etc/ssh/ssh_config
VOLUME /opt/codeforlife-deploy/
WORKDIR /opt/codeforlife-deploy/
