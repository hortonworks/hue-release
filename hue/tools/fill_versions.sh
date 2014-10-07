#!/bin/bash

hue_dir=/usr/lib/hue

# Run only first time
if [ -f ${hue_dir}/VERSIONS ]; then exit; fi

echo "Detecting versions of components..."

function get_version() {
    [ -z $2 ] && RANGE="1-3" || RANGE="$2"

    if which yum &>/dev/null; then
        # RPM
        VERSION=$(yum list ${1}\* | grep "^$1" | awk '{print $2}' | cut -d. -f${RANGE} | sed "s/.[0-9]*-/-/g" | head -n 1)
    elif which zypper &>/dev/null; then
        # SLES
        VERSION=$(zypper search --match-exact -t package --details $1 | grep ' package ' | awk -F'|' '{print $4}')
        VERSION=$(echo $VERSION | cut -d. -f${RANGE}  | sed "s/.[0-9]*-/-/g" | head -n 1)
    elif which aptitude &>/dev/null; then
        # Ubuntu
        VERSION=$(aptitude -F '%p %v#' search "^$1\$" | awk '{print $2}' | cut -d. -f${RANGE} | sed "s/.[0-9]*-/-/g" | head -n 1)
    elif which apt-cache &>/dev/null; then
        # Debian
        VERSION=$(apt-cache show "^$1\$" | grep Version | awk '{print $2}' | cut -d. -f${RANGE} | sed "s/.[0-9]*-/-/g" | head -n 1)
    elif which rpm &>/dev/null; then
        # No yum and zypper => naive check on installed packages (will not work on multi-node deployment)
        VERSION=$(rpm -q --qf "%{VERSION}" `rpm -qa | grep "^$1[_0-9\.xel-]*$"` | cut -d. -f${RANGE} | sed "s/.[0-9]*-/-/g" | head -n 1)
    else
        # something other
        VERSION=""
    fi
    [ -z $VERSION ] && VERSION="can't determine" || echo "$VERSION"
}

# Determining HDP stack components versions
echo "HUE_VERSION=$(get_version hue-common 1-3,7)" | tee ${hue_dir}/VERSIONS
echo "HDP=$(get_version hadoop 4-6)" | tee -a ${hue_dir}/VERSIONS

APPS="Hadoop Pig Hive-Hcatalog Oozie Ambari-server HBase Knox Storm Falcon"
for app in $APPS ; do
    app_name="$(echo $app | tr '[:upper:]' '[:lower:]')"
    app_version="$(get_version ${app_name})"
    echo "${app}=${app_version}" | tee -a ${hue_dir}/VERSIONS
done
