#!/bin/sh -eux
initctl restart tty TTY=/dev/tty5; initctl restart tty TTY=/dev/tty2; true
echo '[[ $(tty) = \"/dev/tty1\" ]] && bash /usr/lib/hue/tools/start_scripts/post_start.sh' >> /root/.bashrc
initctl stop tty TTY=/dev/tty1; initctl start tty-splash TTY=/dev/tty1; true
mv -f /tmp/start-ttys.override /etc/init/start-ttys.override
mv -f /tmp/tty-splash.conf /etc/init/tty-splash.conf
