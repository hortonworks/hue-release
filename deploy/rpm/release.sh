cd $SRC/sandbox-shared

HUE_RELEASE=$(git rev-list --full-history HEAD -- hue start_scripts deploy | wc -l)
TUTORIALS_RELEASE=$(git rev-list --full-history HEAD -- tutorials | wc -l)
echo "New RPM release:"
echo "hue: $HUE_RELEASE"
echo "tutorials: $TUTORIALS_RELEASE"

sed -i -r -e "s/^Release:.*$/Release: $HUE_RELEASE/g" ./deploy/rpm/hue/hue.spec
sed -i -r -e "s/^Release:.*$/Release: $TUTORIALS_RELEASE/g" ./deploy/rpm/tutorials/hue-tutorials.spec
sed -i -r -e "s/^(requires: hue[^-]*-)[0-9]*$/\1$HUE_RELEASE/g" ./deploy/rpm/tutorials/hue-tutorials.spec
