from pprint import pprint
from datetime import datetime, timedelta
import logging

from elasticsearch_dsl import Index
from elasticsearch import helpers
import elasticsearch.exceptions
from elasticsearch_dsl.connections import connections

from cif.store.plugin.indicator import IndicatorManagerPlugin

from .helpers import expand_ip_idx, expand_location
from .filters import filter_build
from .schema import Indicator
from .constants import LIMIT, WINDOW_LIMIT, TIMEOUT, PARTITION

import time

logger = logging.getLogger('cif_elasticsearch')


class IndicatorManager(IndicatorManagerPlugin):
    class Deserializer(object):
        def __init__(self):
            pass

        def loads(self, s, mimetype=None):
            return s

    def __init__(self, *args, **kwargs):
        super(IndicatorManager, self).__init__(*args, **kwargs)

        self.indicators_prefix = 'indicators'
        self.partition = PARTITION
        self.idx = self._current_index()
        self.last_index_check = datetime.now() - timedelta(minutes=5)
        self.handle = connections.get_connection

        self._create_index()

    def flush(self):
        self.handle().indices.flush(index=self._current_index())

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

        if not self.handle().indices.exists(idx):
            index = Index(idx)
            index.aliases(live={})
            index.document(Indicator)
            index.settings(
                max_result_window=WINDOW_LIMIT,
                number_of_shards=3,
                number_of_replicas=2
            )
            index.create()
            self.handle().indices.flush(idx)

        self.last_index_check = datetime.utcnow()
        return idx

    def search(self, token, filters, sort='-reported_at', raw=False,
               timeout=TIMEOUT):
        limit = filters.get('limit', LIMIT)

        s = Indicator.search(index='{}-*'.format(self.indicators_prefix))
        s = s.params(size=limit, timeout=timeout)
        s = s.sort(sort)

        s = filter_build(s, filters, token=token)

        logger.debug(s.to_dict())

        start = time.time()

        rv = self.handle().search(
            index=Indicator.Index.name,
            doc_type=Indicator.Index.doc_type,
            body=s.to_dict(),
            filter_path=['hits.hits._source'],
            **s._params)

        logger.debug('query took: %0.2f' % (time.time() - start))

        if len(rv) == 0:
            return []

        if raw:
            return rv

        return [r['_source'] for r in rv['hits']['hits']]

    def _create_action(self, token, indicator, index):
        expand_ip_idx(indicator)
        expand_location(indicator)

        return {
            '_index': index,
            '_type': Indicator.Index.doc_type,
            '_source': indicator
        }

    def create(self, token, indicators, flush=False):
        index = self._create_index()
        
        helpers.bulk(
            self.handle(),
            [self._create_action(token, i, index) for i in indicators],
            index=self._current_index()
        )

        if flush:
            self.flush()

    def delete(self, token, indicators, flush=False):
        raise NotImplemented('TODO')
