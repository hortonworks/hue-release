export BB="$HOME/rpmbuild"  # base directory

# === create rpmbuild enviromnent ===
mkdir -p $BB/rpm $BB/rpm/BUILD $BB/rpm/RPMS $BB/rpm/RPMS/i386 $BB/rpm/RPMS/i686
mkdir -p $BB/rpm/RPMS/noarch $BB/rpm/SOURCES $BB/rpm/SPECS $BB/rpm/SRPMS $BB/rpm/tmp
