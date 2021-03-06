from pprint import pprint
from datetime import datetime, timedelta
import logging

from elasticsearch_dsl import Index, Search
from elasticsearch import helpers
import elasticsearch.exceptions
from elasticsearch_dsl.connections import connections

from cif.store.plugin.indicator import IndicatorManagerPlugin

from .helpers import expand_ip_idx, expand_location
from .filters import filter_build, filter_build_bulk
from .schema import Indicator
from .constants import LIMIT, WINDOW_LIMIT, TIMEOUT, PARTITION, SHARDS, REPLICAS

import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Deserializer(object):
    def __init__(self):
        pass

    def loads(self, s, mimetype=None):
        return s


class IndicatorManager(IndicatorManagerPlugin):

    def __init__(self, *args, **kwargs):
        super(IndicatorManager, self).__init__(*args, **kwargs)

        self.indicators_prefix = 'indicators'
        self.partition = PARTITION
        self.idx = self._current_index()
        self.last_index_check = datetime.now() - timedelta(minutes=5)
        self.handle = connections.get_connection

        self._create_index(force=True)

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

    def _create_index(self, force=False):
        # https://github.com/csirtgadgets/massive-octo-spice/blob/develop/elasticsearch/observables.json
        # http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch.bulk
        idx = self._current_index()

        # every time we check it does a HEAD req
        if not force and ((datetime.utcnow() - self.last_index_check) < timedelta(minutes=1)):
            return idx

        if not self.handle().indices.exists(idx):
            logger.debug(f"building index: {idx}")
            index = Index(idx)
            index.aliases(live={})
            index.document(Indicator)
            index.settings(
                max_result_window=WINDOW_LIMIT,
                number_of_shards=SHARDS,
                number_of_replicas=REPLICAS
            )
            index.create()
            self.handle().indices.flush(idx)

        self.last_index_check = datetime.utcnow()
        return idx

    def _search_bulk(self, s, filters, token):
        pprint(filters)

        s = s.filt
        return s

    def search(self, token, filters, sort='-reported_at', timeout=TIMEOUT):
        # TODO- pretty sure with larger feeds there's a constant memory leak
        # with the results, so we may need to build a custom de-serializer
        # as we did in v3
        # https://github.com/elastic/elasticsearch-py/blob/master/elasticsearch/helpers/actions.py#L313

        limit = 500
        s = Indicator.search(index=Indicator.Index.name)
        s = s.params(size=limit, timeout=timeout)

        if isinstance(filters, list) and len(filters) > 1:
            s = filter_build_bulk(s, filters, token)
        else:
            limit = filters.get('limit', LIMIT)
            s = filter_build(s, filters, token=token)

        limit = int(limit)
        s = s.sort(sort)
        s = s[:limit]

        start = time.time()

        try:
            rv = s.execute()
        except Exception as e:
            logger.error(e)
            return

        logger.debug(f"hits: {rv.hits.total}")

        if rv.hits.total == 0:
            return

        for x in rv.hits.hits:
            yield x['_source']

        logger.debug('query took: %0.2f' % (time.time() - start))

    @staticmethod
    def _create_action(indicator, index):
        expand_ip_idx(indicator)
        expand_location(indicator)
        indicator['created_at'] = datetime.utcnow()

        return {
            '_index': index,
            '_type': Indicator.Index.doc_type,
            '_source': indicator
        }

    def upsert(self, token, indicators, **kwargs):
        return self.create(token, indicators, **kwargs)

    def create(self, token, indicators, flush=False):
        index = self._create_index()
        
        helpers.bulk(
            self.handle(),
            [self._create_action(i, index) for i in indicators],
            index=self._current_index()
        )

        if flush:
            self.flush()

    def delete(self, token, indicators, flush=False):
        raise NotImplemented('TODO')
