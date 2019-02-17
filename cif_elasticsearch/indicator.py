from pprint import pprint
from datetime import datetime, timedelta
import logging

from elasticsearch_dsl import Index
from elasticsearch import helpers
import elasticsearch.exceptions
from elasticsearch_dsl.connections import connections

from cif.store.plugin.indicator import IndicatorManagerPlugin

from .helpers import expand_ip_idx
from .filters import filter_build
from .constants import LIMIT, WINDOW_LIMIT, TIMEOUT, PARTITION

import time

logger = logging.getLogger('cif.store.elasticsearch')


class IndicatorManager(IndicatorManagerPlugin):
    class Deserializer(object):
        def __init__(self):
            pass

        def loads(self, s, mimetype=None):
            return s

    def __init__(self, *args, **kwargs):
        super(IndicatorManager, self).__init__(*args, **kwargs)

        self.indicators_prefix = kwargs.get('indicators_prefix', 'indicators')
        self.partition = PARTITION
        self.idx = self._current_index()
        self.last_index_check = datetime.now() - timedelta(minutes=5)
        self.handle = connections.get_connection()

        self._create_index()

    def flush(self):
        self.handle.indices.flush(index=self._current_index())

    def _current_index(self):
        dt = datetime.utcnow()

        if self.partition == 'month':  # default partition setting
            dt = dt.strftime('%Y.%m')

        if self.partition == 'day':
            dt = dt.strftime('%Y.%m.%d')

        if self.partition == 'year':
            dt = dt.strftime('%Y')

        return '{}-{}'.format(self.indicators_prefix, dt)

    def _create_index(self):
        # https://github.com/csirtgadgets/massive-octo-spice/blob/develop/elasticsearch/observables.json
        # http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch.bulk
        idx = self._current_index()

        # every time we check it does a HEAD req
        if (datetime.utcnow() - self.last_index_check) < timedelta(minutes=2):
            return idx

        if not self.handle.indices.exists(idx):
            index = Index(idx)
            index.aliases(live={})
            index.doc_type(Indicator)
            index.settings(max_result_window=WINDOW_LIMIT)
            index.create()
            self.handle.indices.flush(idx)

        self.last_index_check = datetime.utcnow()
        return idx

    def search(self, token, filters, sort='reporttime', raw=False,
               timeout=TIMEOUT):
        limit = filters.get('limit', LIMIT)

        s = Indicator.search(index='{}-*'.format(self.indicators_prefix))
        s = s.params(size=limit, timeout=timeout)
        s = s.sort('-reporttime', '-lasttime')

        s = filter_build(s, filters, token=token)

        logger.debug(s.to_dict())

        start = time.time()
        # TODO - convert this to scan and use self.handle.. dunno
        # what they did here..
        try:
            es = connections.get_connection(s._using)
            old_serializer = es.transport.deserializer
            es.transport.deserializer = self.Deserializer()
            rv = es.search(
                index=s._index,
                doc_type=s._doc_type,
                body=s.to_dict(),
                filter_path=['hits.hits._source'],
                **s._params)

            # transport caches this, so the tokens mis-fire
            es.transport.deserializer = old_serializer

        except elasticsearch.exceptions.RequestError as e:
            logger.error(e)
            es.transport.deserializer = old_serializer
            return

        # catch all other es errors
        except elasticsearch.ElasticsearchException as e:
            logger.error(e)
            es.transport.deserializer = old_serializer
            raise ConnectionError

        logger.debug('query took: %0.2f' % (time.time() - start))

        return rv

    def _create_action(self, token, indicator, index):
        expand_ip_idx(indicator)

        yield {
            '_index': index,
            '_type': 'indicator',
            '_source': indicator
        }

    def create(self, token, indicators):
        index = self._create_index()
        
        helpers.bulk(
            self.handle,
            [self._create_action(token, i, index) for i in indicators],
            index=self._current_index()
        )
