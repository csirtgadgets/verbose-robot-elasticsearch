
import pytest
from cif.store import Store
from csirtg_indicator import Indicator
from elasticsearch_dsl.connections import connections
import arrow
from pprint import pprint


def _del_index(idx):
    connections.get_connection().indices.delete(index=idx)

@pytest.yield_fixture
def store():
    try:
        [_del_index(i) for i in ['indicators-*', 'tokens']]

    except Exception as e:
        pass

    with Store(store_type='elasticsearch') as s:

        yield s

    [_del_index(i) for i in ['indicators-*', 'tokens']]


@pytest.yield_fixture
def token(store):
    t = store.store.tokens.create({
        'username': 'test_admin',
        'groups': ['everyone'],
        'read': True,
        'write': True,
        'admin': True
    })

    assert t
    yield t['token']


@pytest.fixture
def indicator():
    return {
        'indicator': 'example.com',
        'tags': ['botnet'],
        'provider': 'csirtgadgets.com',
        'group': 'everyone',
        'last_at': arrow.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'reported_at': arrow.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'itype': 'fqdn',
        'count': 1
    }


@pytest.fixture
def indicator():
    return Indicator(
        indicator='example.com',
        tags='botnet',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    ).__dict__()


@pytest.fixture
def indicator_email():
    return Indicator(
        indicator='user.12.3@example.net',
        tags='botnet',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    ).__dict__()


@pytest.fixture
def indicator_ipv6():
    return Indicator(
        indicator='2001:4860:4860::8888',
        tags='botnet',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    ).__dict__()


@pytest.fixture
def indicator_url():
    return Indicator(
        indicator='http://pwmsteel.com/dhYtebv3',
        tags='exploit',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    ).__dict__()


@pytest.fixture
def indicator_malware():
    return Indicator(
        indicator='d52380918a07322c50f1bfa2b43af3bb54cb33db',
        tags='malware',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    ).__dict__()
