# builds deployment environment and then push changes
FROM ubuntu:14.04
RUN apt-get update -qy
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-client \
                                                      python-mysqldb \
                                                      python-pil \
                                                      python-pip \
                                                      build-essential \
                                                      curl \
                                                      unzip \
                                                      rubygems1.9.1 \
                                                      git
RUN gem install sass --version '3.3.4'
RUN cd /opt; curl -O -s https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.8.zip && \
    unzip -qq google_appengine_1.9.8.zip && rm google_appengine_1.9.8.zip
ENV PATH /opt/google_appengine:$PATH
ADD . /opt/codeforlife-deploy/
ENV TMPDIR /pip
RUN mkdir -p $TMPDIR
RUN mkdir -p /root/.ssh
RUN echo $SSH_KEY > /root/.ssh/id_rsa
RUN pip install -r /opt/codeforlife-deploy/requirements.txt
RUN ls -d /usr/local/lib/python2.7/dist-packages/* | grep -v info | xargs -i cp -R {} /opt/codeforlife-deploy/
RUN chmod +x /opt/codeforlife-deploy/deploy.sh
CMD ["/opt/codeforlife-deploy/deploy.sh"]
