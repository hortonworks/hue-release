set -e
set -v

function tgz() {
    cd `dirname $1`
    tar zcvf `basename $1`.tgz --exclude='.env' `basename $1`
    cd -
}


# === create rpmbuild enviromnent ===
mkdir -p ~/rpm ~/rpm/BUILD ~/rpm/RPMS ~/rpm/RPMS/i386 ~/rpm/RPMS/i686
mkdir -p ~/rpm/RPMS/noarch ~/rpm/SOURCES ~/rpm/SPECS ~/rpm/SRPMS ~/rpm/tmp

cat << EOF > ~/.rpmmacros
%_topdir               $HOME/rpm
%_tmppath              $HOME/rpm/tmp
EOF

# === tgz tutorials ===

tgz `readlink -f ../tutorials`
mv ../tutorials.tgz ~/rpm/SOURCES/

# === tgz hue ===

#make tgz: $ cd /home/sandbox; tar czvf hue.tgz --exclude ".git" hue
[ -f hue.tgz ] || curl http://dl.dropbox.com/u/3926517/hue.tgz -o hue.tgz
cp hue.tgz ~/rpm/SOURCES/

# === spec file ===

cp *.spec ~/rpm/SPECS/


# === build rpm! ===

rpmbuild -ba ~/rpm/SPECS/sandbox-bin.spec --target=x86_64
rpmbuild -ba ~/rpm/SPECS/sandbox-meta.spec
rpmbuild -ba ~/rpm/SPECS/sandbox-src.spec
rpmbuild -ba ~/rpm/SPECS/sandbox-tutorials-files.spec
rpmbuild -ba ~/rpm/SPECS/sandbox-tutorials-sl.spec

mv ~/rpm/RPMS/noarch/*.rpm ./

# === clean all ===
rm -rf ~/rpm
