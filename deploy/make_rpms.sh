set -e
set -v

function tgz() {
    cd `dirname $1`
    tar zcvf `basename $1`.tgz `basename $1`
    cd -
}


# === create rpmbuild enviromnent ===
mkdir -p ~/rpm ~/rpm/BUILD ~/rpm/RPMS ~/rpm/RPMS/i386 ~/rpm/RPMS/i686
mkdir -p ~/rpm/RPMS/noarch ~/rpm/SOURCES ~/rpm/SPECS ~/rpm/SRPMS ~/rpm/tmp

cat << EOF > ~/.rpmmacros
%_topdir               $HOME/rpm
%_tmppath              $HOME/rpm/tmp
EOF

# === make tgzs ===

rm -f ../tutorials/tutorials_app/db/lessons.db

dir=`readlink -f ../tutorials`
cd `dirname $dir`
tar zcvf `basename $dir`.tgz `basename $dir` --exclude=".env"
cd -

mv ../tutorials.tgz ~/rpm/SOURCES/

tgz `readlink -f ../start_scripts`
mv ../start_scripts.tgz ~/rpm/SOURCES/

[ -f .ssh.tar.gz ] || wget -O .ssh.tar.gz https://dl.dropbox.com/s/y4ae019z6944vn3/.ssh.tar.gz?dl=1
cp .ssh.tar.gz ~/rpm/SOURCES/

maven="apache-maven-3.0.4-bin.tar.gz"
[ -f $maven ] || curl http://mirrors.besplatnyeprogrammy.ru/apache/maven/maven-3/3.0.4/binaries/apache-maven-3.0.4-bin.tar.gz -o $maven
cp $maven ~/rpm/SOURCES/

# === tgz hue ===

#make tgz: $ cd /home/sandbox; tar czvf hue.tgz --exclude ".git" hue
[ -f tutorials-env.tgz ] || curl http://dl.dropbox.com/u/3926517/tutorials-env.tgz -o tutorials-env.tgz
cp tutorials-env.tgz ~/rpm/SOURCES/


[ -f hue.tgz ] || curl http://dl.dropbox.com/u/3926517/hue.tgz -o hue.tgz
cp hue.tgz ~/rpm/SOURCES/

# === spec file ===

cp *.spec ~/rpm/SPECS/


# === build rpm! ===

rpmbuild -ba ~/rpm/SPECS/sandbox-bin.spec --target=x86_64
rpmbuild -ba ~/rpm/SPECS/sandbox-meta.spec
#rpmbuild -ba ~/rpm/SPECS/sandbox-src.spec
rpmbuild -ba ~/rpm/SPECS/sandbox-tutorials-files.spec
#rpmbuild -ba ~/rpm/SPECS/sandbox-tutorials-sl.spec

mv ~/rpm/RPMS/noarch/*.rpm ./

# === clean all ===
rm -rf ~/rpm
