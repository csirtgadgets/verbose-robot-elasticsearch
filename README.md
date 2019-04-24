# verbose-robot-elasticsearch
Elasticsearch store plugin for CIFv4


# Getting Started
* Make sure you set the `CIF_ES_NODES` in your env for the es plugin to pickup
* In a new store, running `cif-router` for the first time will auto-create the tokens in the `tokens` index. Check your ES cluster for the correct values.

# Docker
## Make sure you have an initial CIF_TOKEN set
```bash
# os x
$ export CIF_TOKEN=`head -n 25000 /dev/urandom | openssl dgst -sha256`

# ubuntu
$ export CIF_TOKEN=`head -n 25000 /dev/urandom | openssl dgst -sha256 | awk -F ' ' '{print $2}'`
```

## Sample `run.sh`
```bash
#!/bin/bash

# do you have one of these?
# https://csirtg.io
CSIRTG_TOKEN=''

# this is important! make sure this is set even if ES is running in a sep docker container
CIF_ES_NODES=192.168.1.1:9200

# other configs you don't need to worry about
DOCKER_CONFIGS="$(pwd)"
ULIMIT=4096
CIF_STORE_STORE=elasticsearch

if [[ $CIF_TOKEN == "" ]]; then
  echo "$CIF_TOKEN NOT SET IN YOUR ENV"
  exit
fi

docker run \
 -e CIF_ES_NODES=${CIF_ES_NODES} -e CIF_STORE_STORE=${CIF_STORE_STORE} -e CIF_TOKEN=${CIF_TOKEN} -e CSIRTG_TOKEN=${CSIRTG_TOKEN} \
 -e CIF_STORE_TRACE=1 -e CSIRTG_FM_PARSER_TRACE=0 -e CIF_ROUTER_TRACE=1 -d -p 5000:5000 \
 --ulimit nofile=${ULIMIT}:${ULIMIT} \
 -v "${DOCKER_CONFIGS}/data/:/var/lib/cif" \
 -v "${DOCKER_CONFIGS}/logs/:/var/log/cif" \
 --name verbose-robot csirtgadgets/verbose-robot:latest
```

# Standalone
```bash
# make sure your env has the right ES nodes in it
export CIF_ES_NODES=127.0.0.1:9200

$ pip install -r requirements.txt
$ python setup.py install
$ cif-router --store elasticsearch
```

