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

mkdir -p ../tutorials/deploy
cp -R * ../tutorials/deploy

tgz `readlink -f ../tutorials`
mv ../tutorials.tgz ~/rpm/SOURCES/

rm -rf ../tutorials/deploy

# === spec file ===

cp *.spec ~/rpm/SPECS/


# === build rpm! ===
rpmbuild -ba ~/rpm/SPECS/*.spec

mv ~/rpm/RPMS/noarch/*.rpm ./

# === clean all ===
rm -rf ~/rpm
