#!/bin/bash

hue_dir=/usr/lib/hue

function get_version() {
    [ -z $2 ] && RANGE="1-3" || RANGE="$2"
    rpm -q --qf "%{VERSION}" $1 | cut -d. -f${RANGE}
}

# Determining HDP stack versions
echo "HUE_VERSION=$(get_version hue-common)" > ${hue_dir}/VERSIONS
echo "HDP=$(get_version hadoop 4-6)" >> ${hue_dir}/VERSIONS

APPS="Hadoop HCatalog Pig Hive Oozie"
for app in $APPS ; do
  app_name="$(echo $app | tr '[:upper:]' '[:lower:]')"
  app_version="$(get_version ${app_name})"
  echo "${app}=${app_version}" >> ${hue_dir}/VERSIONS
done
