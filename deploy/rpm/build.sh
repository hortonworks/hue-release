set -x
set -e

export SRC=$HOME/rpmbuild/src
export OUT=$HOME/rpmbuild/out
export PATH=$PATH:$SRC/apache-maven-3.0.5/bin/

BRANCH=Caterpillar

# remove all src files (except of repository)
find $SRC -maxdepth 1 | sed "1d" | grep -v "sandbox-shared" | grep -v "tutorials-env" | xargs rm -rf

mkdir -p $SRC $OUT

# uncomment this line and change git_ssh.sh file if you need 
# to specify ssh key!
# export GIT_SSH="`pwd`/git_ssh.sh"

#===== Making sources ======

cd $SRC

[ ! -d $SRC/sandbox-shared ] && git clone git@github.com:/hortonworks/sandbox-shared.git sandbox-shared
(cd sandbox-shared; git reset --hard HEAD; git checkout $BRANCH; git pull origin $BRANCH)

#Tutorials stuff
( 
    cd sandbox-shared

    tar zcf $SRC/start_scripts.tgz start_scripts
    tar zcf $SRC/tutorials.tgz tutorials --exclude=".git"
)

sudo yum -y install createrepo git rpm-build ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi gcc gcc-c++ krb5-devel libxml2-devel libxslt-devel mysql  mysql-devel openldap-devel python-devel python-simplejson sqlite-devel
sudo easy_install virtualenv

mkdir -p tutorials-env && cd tutorials-env
virtualenv .env
(
   source .env/bin/activate
   pip install django==1.4 django-mako gunicorn mysql-python sh
)
tar zcf $SRC/tutorials-env.tgz .env

# Build Hue


mkdir -p $SRC/env/usr/lib
mkdir -p $SRC/env/{$SRC,$OUT}

rm -rf $SRC/hue

cd $SRC
wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
tar xvf apache-maven-3.0.5-bin.tar.gz
rm apache-maven-3.0.5-bin.tar.gz
cd $SRC/sandbox-shared/hue
PREFIX=$SRC make install
#Building started ....
#After it's finished there would be a directory /usr/lib/hue
bash $SRC/hue/tools/relocatable.sh

cd $SRC
tar zcf $SRC/hue.tgz hue


cd $SRC/sandbox-shared/deploy/rpm

#======= Making rpms =======

( #Hue RPM
    cd hue
    cp $SRC/hue.tgz $SRC/start_scripts.tgz ./

    bash make_hue_rpm.sh
    mv *.rpm $OUT/
)

( #Tutorials RPM
    cd tutorials
    cp $SRC/tutorials.tgz $SRC/tutorials-env.tgz ./
    bash make_tutorials_rpm.sh
    mv *.rpm $OUT/
)

unset GIT_SSH

#====== Create repository =====
cd $OUT
createrepo .

set +x

echo "Building repository finished: $OUT"
