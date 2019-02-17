import logging
import os
import traceback
from time import sleep

from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import ConnectionError

from cif.store.plugin import Store

from .indicator import IndicatorManager
from .token import TokenManager

ES_NODES = os.getenv('CIF_ES_NODES', '127.0.0.1:9200')
TRACE = os.environ.get('CIF_ES_TRACE')
TRACE_HTTP = os.getenv('CIF_ES_HTTP_TRACE')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('elasticsearch').setLevel(logging.ERROR)

if TRACE:
    logger.setLevel(logging.DEBUG)

if TRACE_HTTP:
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('elasticsearch').setLevel(logging.DEBUG)


class ES(Store):
    # http://stackoverflow.com/questions/533631/what-is-a-mixin-and-why-are-they-useful

    name = 'elasticsearch'

    def __init__(self, **kwargs):
        self.indicators_prefix = kwargs.get('indicators_prefix', 'indicators')
        self.tokens_prefix = kwargs.get('tokens_prefix', 'tokens')

        connections.create_connection(hosts=kwargs.get('nodes', ES_NODES))

        self._alive = False

        while not self._alive:
            if not self._health_check():
                logger.warn('ES cluster not accessible')
                logger.info('retrying connection in 30s')
                sleep(30)

            self._alive = True

        logger.info('ES connection successful')
        self.tokens = TokenManager()
        self.indicators = IndicatorManager()

    def _health_check(self):
        try:
            x = connections.get_connection().cluster.health()
        except ConnectionError as e:
            logger.warn('elasticsearch connection error')
            logger.error(e)
            return

        except Exception as e:
            logger.error(traceback.print_exc())
            return

        logger.info('ES cluster is: %s' % x['status'])
        return x

    def ping(self, token):
        s = self._health_check()

        if s is None or s['status'] == 'red':
            raise ConnectionError('ES Cluster Issue')

        if self.tokens.read(token) or self.tokens.write(token):
            return True


Plugin = ES
