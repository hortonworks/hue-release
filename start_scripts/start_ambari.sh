#!/bin/bash

touch /root/.start_ambari
make --makefile /home/sandbox/start_scripts/start_deps.mf -B Ambari -j -i

echo "======================================"
echo
echo "Ambari autostart enabled"
echo "To disable auto-start of Ambari do"
echo "  # rm /root/.start_ambari"
echo
echo "======================================"
