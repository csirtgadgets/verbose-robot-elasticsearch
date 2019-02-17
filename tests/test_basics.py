
import logging
import os
import tempfile
from argparse import Namespace
import pytest
from cif.store.plugin import Store
from cifsdk.utils import setup_logging
from elasticsearch_dsl.connections import connections
import arrow

args = Namespace(debug=True, verbose=None)
setup_logging(args)

logger = logging.getLogger(__name__)



