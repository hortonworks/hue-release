wget -O /tmp/videos.tar.gz http://dev2.hortonworks.com.s3.amazonaws.com/videos.tar.gz
mkdir /usr/lib/tutorials/sandbox-tutorials
tar xvf /tmp/videos.tar.gz -C /usr/lib/tutorials/sandbox-tutorials

for file in /usr/lib/tutorials/sandbox-tutorials/local/*.mp4; do 
    mv "$file" `echo $file | sed -r -e 's/([^0-9]*).*/\1.mp4/g'`;
done

exit 0
