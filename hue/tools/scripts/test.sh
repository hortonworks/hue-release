#!/bin/bash

set -e
set -x

if [ ! -e $HOME/.hue_cache ]; then
  mkdir -p $HOME/.hue_cache
fi;

check_mtime() {
  MTIME_FILE=${1}
  MTIME=$( curl -Is ${2} | awk 'BEGIN {FS=":"} { if ($1 == "Last-Modified") { print substr($2,2) } }' )

  if echo "${MTIME}" | diff ${MTIME_FILE} - > /dev/null; then
    return 0
  else
    echo ${MTIME} > ${MTIME_FILE}
    return 1
  fi;
}

HUE_ROOT=${HUE_HOME:-/usr/lib/hue}

export REPO_TRACE=1
##########
#
# Use $HDP_URL to control where to download Hadoop.
# If not specified, it uses the $HDP variable to select an archive location.
#

HDP_URL=${HDP_URL:-http://public-repo-1.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/updates/2.1.5.0/tars/hadoop-2.4.0.2.1.5.0-695.tar.gz}

HDP_TGZ=$(basename $HDP_URL)
HDP_VERSION=${HDP_TGZ/.tar.gz/}
HDP_SHORT_VERSION=${HDP_VERSION/hadoop-/}
HDP_CACHE="$HOME/.hue_cache/${HDP_TGZ}"
HDP_MTIME_FILE="$HOME/.hue_cache/.hdp_mtime"

build_hadoop() {
  if ! check_mtime ${HDP_MTIME_FILE} ${HDP_URL} || [ ! -f $HDP_CACHE ]; then
    echo "Downloading $HDP_URL..."
    wget $HDP_URL -O $HDP_CACHE
  fi

  HADOOP_DIR=$HUE_ROOT/ext/hadoop
  export YARN_HOME="$HADOOP_DIR/${HDP_VERSION}"
  export HADOOP_HDFS_HOME="$HADOOP_DIR/${HDP_VERSION}/share/hadoop/hdfs"
  export HADOOP_BIN="$HADOOP_DIR/${HDP_VERSION}/bin/hadoop"
  export HADOOP_MAPRED_HOME="$HADOOP_DIR/${HDP_VERSION}/share/hadoop/mapreduce2"
  export HADOOP_MAPRED_BIN="$HADOOP_DIR/${HDP_VERSION}/bin/mapred"

  mkdir -p $HADOOP_DIR
  rm -rf "$HADOOP_DIR/${HDP_VERSION}"
  echo "Unpacking $HDP_CACHE to $HADOOP_DIR"
  tar -C $HADOOP_DIR -xzf $HDP_CACHE
  ln -sf $HADOOP_DIR/${HDP_VERSION} $HADOOP_DIR/hadoop
  # For Hive
  ln -sf $HADOOP_DIR/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-core-*.jar $HADOOP_DIR/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-core.jar
  ln -sf $HADOOP_DIR/hadoop/share/hadoop/common/hadoop-common-*-SNAPSHOT.jar $HADOOP_DIR/hadoop/share/hadoop/common/hadoop-common.jar
  ln -sf $HADOOP_DIR/hadoop/share/hadoop/common/lib/hadoop-auth-*-SNAPSHOT.jar $HADOOP_DIR/hadoop/share/hadoop/common/lib/hadoop-auth.jar
  ln -sf $HADOOP_DIR/hadoop/share/hadoop/hdfs/hadoop-hdfs-${HDP_SHORT_VERSION}.jar  $HADOOP_DIR/hadoop/share/hadoop/hdfs/hadoop-hdfs.jar
  # For MR2
  ln -sf "$HADOOP_DIR/${HDP_VERSION}/share/hadoop/mapreduce2" "$HADOOP_DIR/${HDP_VERSION}/share/hadoop/mapreduce"
}

##########

HIVE_URL=${HIVE_URL:-http://public-repo-1.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/updates/2.1.5.0/tars/apache-hive-0.13.0.2.1.5.0-695-bin.tar.gz}

HIVE_TGZ=$(basename $HIVE_URL)
HIVE_VERSION=${HIVE_TGZ/.tar.gz/}
HIVE_CACHE="$HOME/.hue_cache/${HIVE_TGZ}"
HIVE_MTIME_FILE="$HOME/.hue_cache/.hive_mtime"

build_hive() {
  if ! check_mtime ${HIVE_MTIME_FILE} ${HIVE_URL} || [ ! -f $HIVE_CACHE ]; then
    echo "Downloading $HIVE_URL..."
    wget $HIVE_URL -O $HIVE_CACHE
  fi

  HIVE_DIR=$HUE_ROOT/ext/hive
  export HIVE_HOME="$HIVE_DIR/${HIVE_VERSION}"

  mkdir -p $HIVE_DIR
  rm -rf $HIVE_HOME
  echo "Unpacking $HIVE_CACHE to $HIVE_DIR"
  tar -C $HIVE_DIR -xzf $HIVE_CACHE
  ln -sf $HIVE_DIR/${HIVE_VERSION} $HIVE_DIR/hive
  export HIVE_CONF_DIR=$HIVE_HOME/conf

  # Weird HADOOP_HOME, creating a HADOOP_HIVE_HOME
  #sed -i'.bk' "s|HADOOP=\$HADOOP_HOME/bin/hadoop|HADOOP=\$HADOOP_HIVE_HOME/bin/hadoop|g" $HIVE_HOME/bin/hive
}

##########
OOZIE_URL=${OOZIE_URL:-http://public-repo-1.hortonworks.com.s3.amazonaws.com/HDP/centos6/2.x/updates/2.1.5.0/tars/oozie-4.0.0.2.1.5.0-695-distro.tar.gz}

OOZIE_TGZ=$(basename $OOZIE_URL)
OOZIE_VERSION=${OOZIE_TGZ/-distro.tar.gz/}
OOZIE_CACHE="$HOME/.hue_cache/${OOZIE_TGZ}"
OOZIE_MTIME_FILE="$HOME/.hue_cache/.oozie_mtime"

build_oozie() {
  if ! check_mtime ${OOZIE_MTIME_FILE} ${OOZIE_URL} || [ ! -f $OOZIE_CACHE ]; then
    echo "Downloading $OOZIE_URL..."
    wget $OOZIE_URL -O $OOZIE_CACHE
  fi

  OOZIE_DIR=$HUE_ROOT/ext/oozie
  export OOZIE_HOME="$OOZIE_DIR/${OOZIE_VERSION}"

  mkdir -p $OOZIE_DIR
  rm -rf $OOZIE_HOME
  echo "Unpacking $OOZIE_CACHE to $OOZIE_DIR"
  tar -C $OOZIE_DIR -xzf $OOZIE_CACHE
  export OOZIE_CONF_DIR=$OOZIE_HOME/conf

  rm -rf $OOZIE_DIR/oozie
  ln -sf $OOZIE_DIR/${OOZIE_VERSION} $OOZIE_DIR/oozie

  # mkdir -p $OOZIE_HOME/libext
  # tar -C $OOZIE_HOME/libext -zxvf $OOZIE_HOME/oozie-hadooplibs-*.tar.gz
  # HADOOP_LIB=`echo "${HDP_VERSION}" | sed -r 's/hadoop/hadooplib/g'`
  # cp $OOZIE_HOME/libext/oozie-*/hadooplibs/${HADOOP_LIB}*/*jar $OOZIE_HOME/libext/
  # tar -C $OOZIE_HOME -zxvf $OOZIE_HOME/oozie-examples.tar.gz
  # cp  $OOZIE_HOME/oozie-sharelib-*-yarn.tar.gz $OOZIE_HOME/oozie-sharelib.tar.gz

  $OOZIE_HOME/bin/oozie-setup.sh prepare-war
  $OOZIE_HOME/bin/ooziedb.sh create -sqlfile oozie.sql -run
}

build_hadoop
build_hive
build_oozie

$HUE_ROOT/build/env/bin/hue test "$@"
