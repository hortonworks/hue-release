#!/bin/sh

#   This script generates ssl private key and self-signed certificate
#   and place them under /etc/ssl/hue.key and /etc/ssl/hue.crt accordingly.
#
#   To use https instead http for hue there is a need to correct hue.ini config file
#   and assign proper values for ssl_certificate and ssl_private_key as shown below:
#
#   # Filename of SSL Certificate
#   ssl_certificate=/etc/ssl/hue.crt
#
#   # Filename of SSL RSA Private Key
#   ssl_private_key=/etc/ssl/hue.key
#

TMP_DIR=/tmp
KEY_TMP=$TMP_DIR/server.key
KEY_EMPTY_TMP=$TMP_DIR/server.key.emp
CSR_TMP=$TMP_DIR/server.csr
CRT_TMP=$TMP_DIR/server.crt

KEY_DEST=/etc/ssl/hue.key
CRT_DEST=/etc/ssl/hue.crt

echo "Step 1: Generating a Private Key"
echo
openssl genrsa -des3 -out $KEY_TMP 1024

echo
echo "Step 2: Generating a CSR (Certificate Signing Request)"
echo
openssl req -new -key $KEY_TMP -out $CSR_TMP

echo
echo "Step 3: Removing Passphrase from Key"
echo
cp $KEY_TMP $KEY_EMPTY_TMP
openssl rsa -in $KEY_EMPTY_TMP -out $KEY_TMP

echo
echo "Step 4: Generating a Self-Signed Certificate"
echo
openssl x509 -req -days 365 -in $CSR_TMP -signkey $KEY_TMP -out $CRT_TMP

echo
echo "Step 5: Installing the Private Key and Certificate"
echo

if [ -f $KEY_TMP ] && [ -f $CSR_TMP ] && [ -f $CRT_TMP ] && [ -f $KEY_EMPTY_TMP ] ; then
	mv $CRT_TMP $CRT_DEST
	mv $KEY_TMP $KEY_DEST
	rm -f $CSR_TMP
	rm -f $KEY_EMPTY_TMP
	echo
	echo "SUCCESS"
else
	echo
	echo "FAILED"
fi