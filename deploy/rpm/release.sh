cd $SRC/sandbox-shared

HUE_RELEASE=$(git rev-list --full-history HEAD -- hue deploy | wc -l)
TUTORIALS_RELEASE=$(git rev-list --full-history HEAD -- tutorials start_scripts deploy | wc -l)

LAST_HASH=$(git log -n 1 --format="%h")
LAST_UNIX_TIMESTAMP=$(git log -n 1 --format="%at")
LAST_TIMESTAMP=$(date -d @$LAST_UNIX_TIMESTAMP -u "+%H:%M %m/%d/%y")

echo "New RPM release:"
echo "hue: $HUE_RELEASE"
echo "tutorials: $TUTORIALS_RELEASE"
echo "sandbox: $LAST_HASH $LAST_TIMESTAMP"

export SANDBOX_TIMESTAMP="$LAST_HASH $LAST_TIMESTAMP"

sed -i -r -e "s/^Release:.*$/Release: $HUE_RELEASE/g" ./deploy/rpm/hue/hue.spec
sed -i -r -e "s/^Release:.*$/Release: $TUTORIALS_RELEASE/g" ./deploy/rpm/tutorials/hue-tutorials.spec
# sed -i -r -e "s/^(requires: hue[^-]*-)[0-9]*$/\1$HUE_RELEASE/g" ./deploy/rpm/tutorials/hue-tutorials.spec
