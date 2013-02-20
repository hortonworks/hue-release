# === create rpmbuild enviromnent ===
mkdir -p ~/rpm ~/rpm/BUILD ~/rpm/RPMS ~/rpm/RPMS/i386 ~/rpm/RPMS/i686
mkdir -p ~/rpm/RPMS/noarch ~/rpm/SOURCES ~/rpm/SPECS ~/rpm/SRPMS ~/rpm/tmp

cat << EOF > ~/.rpmmacros
%_topdir               $HOME/rpm
%_tmppath              $HOME/rpm/tmp
EOF
