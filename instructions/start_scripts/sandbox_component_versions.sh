#!/bin/sh

SANDBOX_VERSIONS_FILE="/tmp/sandbox_component_versions.info"

find /usr -name "pig-*jar" -exec basename {} \; | grep -P "pig-[0-9\-.]*\.jar" | head -n 1 > $SANDBOX_VERSIONS_FILE
find /usr -name "hcatalog-*jar" -exec basename {} \; | grep -P "hcatalog-[0-9\-.]*\.jar" | head -n 1 >> $SANDBOX_VERSIONS_FILE
find /usr -name "hive-cli*jar" -exec basename {} \; | grep -P "hive-cli-[0-9\-.]*\.jar" | head -n 1 >> $SANDBOX_VERSIONS_FILE
echo "sandbox-1.0" >> $SANDBOX_VERSIONS_FILE
echo "tutorials-1.0.001" >> $SANDBOX_VERSIONS_FILE

