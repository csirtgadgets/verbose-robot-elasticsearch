# verbose-robot-elasticsearch
Elasticsearch store plugin for CIFv4


# Getting Started
* Make sure you set the `CIF_ES_NODES` in your env for the es plugin to pickup
* In a new store, running `cif-router` for the first time will auto-create the tokens in the `tokens` index. Check your ES cluster for the correct values.

```bash
# make sure your env has the right ES nodes in it
export CIF_ES_NODES=127.0.0.1:9200

$ pip install -r requirements.txt
$ python setup.py install
$ cif-router --store elasticsearch
```
