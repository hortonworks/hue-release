set -x
set -e

export SRC=$HOME/rpmbuild/src
export OUT=$HOME/rpmbuild/out
export PATH=$PATH:$SRC/apache-maven-3.0.5/bin/

BRANCH=Caterpillar

# remove all src files (except of repository)
find $SRC -maxdepth 1 | sed "1d" | grep -v -e "sandbox-shared" -e "tutorials-env" -e "apache-maven-3.0.5" | xargs rm -rf

mkdir -p $SRC $OUT

# uncomment this line and change git_ssh.sh file if you need 
# to specify ssh key!
# export GIT_SSH="`pwd`/git_ssh.sh"

sudo yum -y install createrepo git rpm-build mysql-devel openldap-devel python-simplejson sqlite-devel

#===== Making sources ======

cd $SRC

[ ! -d $SRC/sandbox-shared ] && git clone git@github.com:/hortonworks/sandbox-shared.git sandbox-shared
(cd sandbox-shared; git reset --hard HEAD^; git clean -df; git fetch; git checkout $BRANCH; git pull origin $BRANCH;

    # comment out to leave release numbers as in repository
    source ./deploy/rpm/release.sh;
    )

#Tutorials stuff
( 
    cd sandbox-shared

    tar zcf $SRC/start_scripts.tgz start_scripts
    tar zcf $SRC/tutorials.tgz tutorials --exclude=".git"
)

# sudo yum -y install ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi gcc gcc-c++ krb5-devel libxml2-devel libxslt-devel mysql python-devel
sudo easy_install virtualenv

mkdir -p tutorials-env && cd tutorials-env
virtualenv .env
(
   source .env/bin/activate
   pip install django==1.4 django-mako gunicorn mysql-python sh
)
tar zcf $SRC/tutorials-env.tgz .env

# Build Hue

<<COMMENT
rm -rf $SRC/hue

cd $SRC

if [ ! -d "apache-maven-3.0.5" ]; then
    wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
    tar xvf apache-maven-3.0.5-bin.tar.gz
    rm apache-maven-3.0.5-bin.tar.gz
fi

cd $SRC/sandbox-shared/hue
PREFIX=$SRC make install
#Building started ....
#After it's finished there would be a directory /usr/lib/hue
bash $SRC/hue/tools/relocatable.sh

cd $SRC
tar zcf $SRC/hue.tgz hue
COMMENT

echo "making rpms"

#======= Making rpms =======

cd $SRC/sandbox-shared/deploy/rpm

<<COMMENT
( #Hue RPM
    cd hue
    cp $SRC/hue.tgz $SRC/start_scripts.tgz ./

    bash make_hue_rpm.sh
    mv *.rpm $OUT/
)
COMMENT

( #Tutorials RPM
    cd tutorials
    cp $SRC/tutorials.tgz $SRC/tutorials-env.tgz ./
    cp $SRC/start_scripts.tgz ./
    bash make_tutorials_rpm.sh
    mv *.rpm $OUT/
)

unset GIT_SSH

#====== Create repository =====
#cd $OUT
#createrepo .

#set +x

#echo "Building repository finished: $OUT"
