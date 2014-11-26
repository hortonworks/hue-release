if [ $# -ne 1 ]; then
    echo "Usage: $0 <user>"
    exit 1
fi
user=$1
set -x

runuser -l $user -c "/usr/bin/hbase shell"
