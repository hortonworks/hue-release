#!/bin/bash

kill `cat /var/run/solr.pid`
echo "Solr stopped!"
