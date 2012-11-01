#!/bin/sh

PATCHES_DIR=`pwd`


#       
# PRECONDITIONS
#
if [ "$#" = "0" ]
then
    echo "Please provide required parameter 'hue home directory' (i.e. ./apply.sh /home/hue )"
    exit 1
fi

cd $1
find $PATCHES_DIR -name "*.patch" -exec patch -p0 -i {} \;
