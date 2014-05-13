FROM ambari/common

ADD puppet/ /tmp/puppet

ADD start.sh /opt/start.sh

RUN rpm -ivh https://yum.puppetlabs.com/el/6/products/x86_64/puppetlabs-release-6-7.noarch.rpm

RUN yum install -y puppet

CMD ["/bin/bash", "/opt/start.sh"]