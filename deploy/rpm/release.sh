REPOQUERY="repoquery --disablerepo='*' --enablerepo='sandbox' --nvr"

yum clean all --disablerepo='*' --enablerepo='sandbox'

cd $SRC/sandbox-shared

HUE_RELEASE=$((`$REPOQUERY hue | cut -d- -f3` + 1))
TUTORIALS_RELEASE=$((`$REPOQUERY hue-tutorials | cut -d- -f4` + 1))
echo "New RPM release:"
echo "hue: $HUE_RELEASE"
echo "tutorials: $TUTORIALS_RELEASE"

sed -i -r -e "s/^Release:.*$/Release: $HUE_RELEASE/g" ./deploy/rpm/hue/hue.spec
sed -i -r -e "s/^Release:.*$/Release: $TUTORIALS_RELEASE/g" ./deploy/rpm/tutorials/hue-tutorials.spec
