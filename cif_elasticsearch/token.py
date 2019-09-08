import arrow
from pprint import pprint
import logging
import os

from elasticsearch_dsl import Index
import elasticsearch.exceptions
from elasticsearch_dsl.connections import connections


from cif.store.plugin.token import TokenManagerPlugin
from .schema import Token
from .constants import SHARDS, REPLICAS

logger = logging.getLogger(__name__)

CONFLICT_RETRIES = os.getenv('CIF_STORE_ES_CONFLICT_RETRIES', 5)
CONFLICT_RETRIES = int(CONFLICT_RETRIES)


class TokenManager(TokenManagerPlugin):
    def __init__(self, *args, **kwargs):
        super(TokenManager, self).__init__(**kwargs)

        self.handle = connections.get_connection
        self.index = 'tokens'

        self._create_index()

    def _create_index(self):
        if self.handle().indices.exists(self.index):
            return

        index = Index(self.index)
        index.settings(
            number_of_shards=1,  # shoudn't ever need more than 1
            number_of_replicas=REPLICAS  # this should scale with the indicators index
        )
        index.document(Token)
        index.create()
        self.handle().indices.flush(self.index)

    def search(self, data, raw=False):
        s = Token.search()

        for k in ['token', 'username', 'admin', 'write', 'read']:
            if not data.get(k):
                continue

            if isinstance(data[k], bytes):
                data[k] = data[k].decode('utf-8')

            s = s.filter('term', **{k: data[k]})

        try:
            rv = s.execute()
        except elasticsearch.exceptions.NotFoundError as e:
            logger.error(e)
            return

        if rv.hits.total == 0:
            return

        for x in rv.hits.hits:
            if raw:
                yield x

            else:
                yield x['_source']

    def create(self, data):
        logger.debug(data)
        for v in ['admin', 'read', 'write']:
            if data.get(v):
                data[v] = True

        if data.get('token') is None:
            data['token'] = self._generate()

        data['created_at'] = arrow.utcnow().datetime

        t = Token(**data)

        if t.save():
            self.handle().indices.flush(index='tokens')
            return t.to_dict()

    def delete(self, data):
        if not (data.get('token') or data.get('username')):
            return 'username or token required'

        rv = self.search(data, raw=True)

        if not rv:
            return 0

        for t in rv:
            t = Token.get(t['_id'])
            t.delete()

        self.handle().indices.flush(index='tokens')
        return len(list(rv))

    def edit(self, data):
        if not data.get('token'):
            return 'token required for updating'

        d = list(self.search({'token': data['token']}))
        if not d:
            return 'token not found'

        d.update(fields=data)
        self.handle().indices.flush(index='tokens')

    def update_last_activity_at(self, token, timestamp=arrow.utcnow().datetime):
        if isinstance(timestamp, str):
            timestamp = arrow.get(timestamp).datetime

        if self._cache_check(token):
            if self._cache[token].get('last_activity_at'):
                return self._cache[token]['last_activity_at']

            self._cache[token]['last_activity_at'] = timestamp
            return timestamp

        rv = list(self.search({'token': token}, raw=True))

        try:
            rv = Token.get(rv[0]['_id'])

        except Exception as e:
            logger.error(e, exc_info=True)
            return timestamp

        try:
            rv.update(last_activity_at=timestamp)
            self._cache[token] = rv.to_dict()
            self._cache[token]['last_activity_at'] = timestamp

        except elasticsearch.exceptions.ConflictError:
            # another thread beat us to it...
            pass

        except Exception as e:
            logger.error(e)

        return timestamp
