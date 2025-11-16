#!/bin/bash

#Usage: ./script.sh <consul_server_ip_address>

SERVER_IP="$1"
sudo apt-get update -y
sudo apt-get install -y unzip gnupg2 curl wget vim

CONSUL_VERSION="1.21.0"
wget "https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip"
unzip "consul_${CONSUL_VERSION}_linux_amd64.zip"
sudo mv consul /usr/local/bin/

CONSUL_USER="consul"
CONSUL_GROUP="consul"
DATA_DIR="/var/lib/consul"
CONFIG_DIR="/etc/consul.d"

sudo groupadd --system "${CONSUL_GROUP}"
sudo useradd -s /sbin/nologin --system -g "${CONSUL_GROUP}" "${CONSUL_USER}"

sudo mkdir -p "${DATA_DIR}"
sudo mkdir -p "${CONFIG_DIR}"

sudo chown -R "${CONSUL_USER}:${CONSUL_GROUP}" "${DATA_DIR}"
sudo chmod -R 775 "${DATA_DIR}"
sudo chown -R "${CONSUL_USER}:${CONSUL_GROUP}" "${CONFIG_DIR}"

SYSTEMD_FILE="/etc/systemd/system/consul.service"

echo "[Unit]
Description=Consul Service Discovery Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${CONSUL_USER}
Group=${CONSUL_GROUP}
ExecStart=/usr/local/bin/consul agent -server -ui \
    -advertise=${SERVER_IP} \
    -bind=${SERVER_IP} \
    -data-dir=${DATA_DIR} \
    -node=consul-01 \
    -config-dir=${CONFIG_DIR}
ExecReload=/bin/kill -HUP \$MAINPID
KillSignal=SIGINT
TimeoutStopSec=5
Restart=on-failure
SyslogIdentifier=consul

[Install]
WantedBy=multi-user.target" | sudo tee "${SYSTEMD_FILE}"
  ENCRYPT_KEY=$(consul keygen)

echo "{
  \"bootstrap\": true,
  \"server\": true,
  \"log_level\": \"DEBUG\",
  \"enable_syslog\": true,
  \"datacenter\": \"server1\",
  \"addresses\": {\"http\": \"0.0.0.0\"},
  \"bind_addr\": \"${SERVER_IP}\",
  \"node_name\": \"ubuntu2404\",
  \"data_dir\": \"${DATA_DIR}\",
  \"acl_datacenter\": \"server1\",
  \"acl_default_policy\": \"allow\",
  \"encrypt\": \"${ENCRYPT_KEY}\"
}" | sudo tee "${CONFIG_DIR}/config.json"

sudo systemctl start consul
sudo systemctl enable consul
