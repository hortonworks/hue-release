set -x
set -e

export SRC=$HOME/rpmbuild/src
export OUT=$HOME/rpmbuild/out

rm -rf $SRC
mkdir -p $SRC $OUT

# uncomment this line and change git_ssh.sh file if you need 
# to specify ssh key!
# export GIT_SSH="`pwd`/git_ssh.sh"

#===== Making sources ======

cd $SRC

git clone git@github.com:/hortonworks/sandbox-shared.git sandbox-shared
(cd sandbox-shared; git checkout Caterpillar;)

#Tutorials stuff
( 
    cd sandbox-shared

    tar zcf $SRC/start_scripts.tgz start_scripts
    tar zcf $SRC/tutorials.tgz tutorials --exclude=".git"
)

yum -y install createrepo git rpm-build ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi gcc gcc-c++ krb5-devel libxml2-devel libxslt-devel mysql  mysql-devel openldap-devel python-devel python-simplejson sqlite-devel
easy_install virtualenv

mkdir -p tutorials-env && cd tutorials-env
virtualenv .env
(
   source .env/bin/activate
   pip install django==1.4 django-mako gunicorn mysql-python sh
)
tar zcf $SRC/tutorials-env.tgz .env

# Build Hue

    list="bin,dev,etc,lib,lib64,proc,sbin,sys,usr,var,root"
    IFS=$' ,'; for x in `echo $list`; do
        mkdir -p $SRC/env/$x
        mount --bind /$x $SRC/env/$x
    done
    mkdir -p $SRC/env/home/sandbox
    mkdir -p $SRC/env/{$SRC,$OUT}

export SRC=$HOME/rpmbuild/src
export OUT=$HOME/rpmbuild/out
export PATH=$PATH:$SRC/apache-maven-3.0.5/bin/

    chroot $SRC/env /bin/bash -- << END_OF_CHROOT

set -x
set -e

cd $SRC
wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
tar xvf apache-maven-3.0.5-bin.tar.gz
rm apache-maven-3.0.5-bin.tar.gz
cd $SRC/sandbox-shared/hue
PREFIX=/home/sandbox make install
#Building started ....
#After it's finished there would be a directory /home/sandbox/hue
bash /home/sandbox/hue/tools/relocatable.sh

END_OF_CHROOT

    IFS=$', '; for x in `echo $list`; do
        umount $SRC/env/$x
    done

    cd $SRC/env/home/sandbox
    tar zcf $SRC/hue.tgz hue


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

    bash make_hue_rpm.sh
    mv *.rpm $OUT/
)

unset GIT_SSH

#====== Create repository =====
cd $OUT
createrepo .

set +x

echo "Building repository finished: $OUT"