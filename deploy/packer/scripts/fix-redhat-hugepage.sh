#!/bin/bash -eux

##Redhat bug fix: https://bugzilla.redhat.com/show_bug.cgi?id=805593
echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag
echo no > /sys/kernel/mm/redhat_transparent_hugepage/khugepaged/defrag
