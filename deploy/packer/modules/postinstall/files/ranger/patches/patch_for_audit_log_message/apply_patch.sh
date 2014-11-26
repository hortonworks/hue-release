#!/bin/bash
cd `dirname $0`
for i in `find / -name "*audit*.jar" 2>/dev/null`; do
    echo "Patching $i..."
    jar vfu $i META-INF
    chmod 777 $i
done