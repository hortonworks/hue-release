cd $SRC/sandbox-shared

TUTORIALS_RELEASE=${BUILD_NUMBER}

LAST_HASH=$(git log -n 1 --format="%h")
LAST_UNIX_TIMESTAMP=$(git log -n 1 --format="%at")
LAST_TIMESTAMP=$(date -d @$LAST_UNIX_TIMESTAMP -u "+%H:%M %m-%d-%y")


echo "New RPM release:"
echo "tutorials: $TUTORIALS_RELEASE"
echo "sandbox: $LAST_HASH $LAST_TIMESTAMP"

export SANDBOX_TIMESTAMP="$LAST_HASH $LAST_TIMESTAMP"

sed -i -r -e "s/^Release:.*$/Release: $TUTORIALS_RELEASE/g" ./deploy/rpm/tutorials/hue-tutorials.spec
sed -i -r -e "s/\%\{sandbox_timestamp\}/$SANDBOX_TIMESTAMP/g" ./deploy/rpm/tutorials/hue-tutorials.spec
