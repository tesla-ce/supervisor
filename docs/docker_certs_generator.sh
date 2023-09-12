#!/bin/bash

# Configuration
export PUBLIC_DNS=dev.tesla-ce.eu
export PUBLIC_IP=213.73.42.33
export PRIVATE_IP=192.168.11.11

mkdir docker-ca
chmod 0700 docker-ca/
cd docker-ca/

# CA key
openssl genrsa -aes256 -out ca-key.pem 2048
# CA certificate
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem

# Server key
openssl genrsa -out server-key.pem 2048
# Server CSR on DNS name
openssl req -subj "/CN==${PUBLIC_DNS}" -new -key server-key.pem -out server.csr
# Alts on IPs
echo "subjectAltName = IP:${PUBLIC_IP},IP:${PRIVATE_IP},IP:127.0.0.1" > extfile.cnf
# Server certificate
openssl x509 -req -days 3650 -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -extfile extfile.cnf

# Client key
openssl genrsa -out client-key.pem 2048
# Client CSR
openssl req -subj '/CN=client' -new -key client-key.pem -out client.csr
# clientAuth
echo extendedKeyUsage = clientAuth > extfile.cnf
# Client certificate
openssl x509 -req -days 3650 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out client-cert.pem -extfile extfile.cnf

# Securing
chmod -v 0400 *-key.pem
chmod -v 0444 ca.pem *-cert.pem