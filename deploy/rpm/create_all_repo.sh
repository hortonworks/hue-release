#!/bin/bash

set -v

mkdir -p ~/repo

(cd hue; bash make_hue_rpm.sh) #&> hue_rpm.log #& echo $! >~/1.pid
(cd tutorials; bash make_tutorials_rpm.sh) #&> tutorials_rpm.log #& echo $! >~/2.pid

(bash make_meta_rpm.sh) #&> meta_rpm.log #& echo $! >~/3.pid


#wait $(<~/1.pid) $(<~/2.pid) $(<~/3.pid)
#rm ~/*.pid

mv hue/*.rpm tutorials/*.rpm *.rpm ~/repo/

cd ~/repo
createrepo .
