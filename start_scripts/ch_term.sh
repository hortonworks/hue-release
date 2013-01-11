while true; do
	c=0;
	while [ ! "x$c" == $(echo -e "x\t") ]; do
		read -s -n 1 c;
	done;
	chvt 2;
done;