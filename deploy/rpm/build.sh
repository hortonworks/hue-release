set -x
set -e

SRC=~/rpmbuild/src
OUT=~/rpmbuild/out

rm -rf $SRC
mkdir -p $SRC $OUT

# uncomment this line and change git_ssh.sh file if you need 
# to specify ssh key!
# export GIT_SSH="`pwd`/git_ssh.sh"

#===== Making sources ======

cd $SRC
git clone git@github.com:/hortonworks/sandbox-shared.git sandbox-shared

#Tutorials stuff
( 
    cd sandbox-shared
    git checkout Caterpillar

    tar zcf $SRC/start_scripts.tgz start_scripts
    tar zcf $SRC/tutorials.tgz tutorials --exclude=".git"
)

mkdir -p tutorials-env && cd tutorials-env
virtualenv .env
(
    source .env/bin/activate
    pip install django==1.4 django-mako gunicorn mysql-python sh
)
tar zcf $SRC/tutorials-env.tgz .env

# Build Hue
( 
    yum -y install git ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi gcc gcc-c++ krb5-devel libxml2-devel libxslt-devel mysql  mysql-devel openldap-devel python-devel python-simplejson sqlite-devel
    useradd sandbox
    su - sandbox
    cd /home/sandbox
    wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
    tar xvf apache-maven-3.0.5-bin.tar.gz
    rm apache-maven-3.0.5-bin.tar.gz
    export PATH=$PATH:/home/sandbox/apache-maven-3.0.5/bin/
    cd sandbox-shared
    git checkout Caterpillar
    cd hue
    PREFIX=/home/sandbox make install
    #Building started ....
    #After it's finished there would be a directory /home/sandbox/hue
    bash /home/sandbox/tools/relocatable.sh


    cd /home/sandbox
    tar zcf $SRC/hue.tgz hue
)

cd $SRC/sandbox-shared/deploy/rpm

#======= Making rpms =======

( #Tutorials RPM
    cd tutorials
    cp $SRC/tutorials.tgz $SRC/tutorials-env.tgz ./
    bash make_tutorials_rpm.sh
    mv *.rpm $OUT/
)

( #Meta-RPM
    bash make_meta_rpm.sh
    mv *.rpm $OUT/
)

( #Hue RPM
    cd hue
    cp $SRC/hue.tgz $SRC/start_scripts.tgz ./
    [ -f .ssh.tar.gz ] || curl $SSH_URL -o .ssh.tar.gz

    bash make_hue_rpm.sh
    mv *.rpm $OUT/
)

unset GIT_SSH

#====== Create repository =====
cd $OUT
createrepo .
