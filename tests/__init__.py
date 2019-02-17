
import pytest
from cif.store import Store
from csirtg_indicator import Indicator
from elasticsearch_dsl.connections import connections
import arrow


@pytest.yield_fixture
def store():
    with Store(store_type='elasticsearch', nodes='127.0.0.1:9200') as s:
        s._load_plugin(nodes='127.0.0.1:9200')
        try:
            connections.get_connection().indices.delete(index='indicators-*')
            connections.get_connection().indices.delete(index='tokens')
        except Exception as e:
            pass
        yield s

    assert connections.get_connection().indices.delete(index='indicators-*')
    assert connections.get_connection().indices.delete(index='tokens')


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
    )


@pytest.fixture
def indicator_email():
    return Indicator(
        indicator='user.12.3@example.net',
        tags='botnet',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    )


@pytest.fixture
def indicator_ipv6():
    return Indicator(
        indicator='2001:4860:4860::8888',
        tags='botnet',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    )

@pytest.fixture
def indicator_url():
    return Indicator(
        indicator='http://pwmsteel.com/dhYtebv3',
        tags='exploit',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    )

@pytest.fixture
def indicator_malware():
    return Indicator(
        indicator='d52380918a07322c50f1bfa2b43af3bb54cb33db',
        tags='malware',
        provider='csirtg.io',
        group='everyone',
        lasttime=arrow.utcnow().datetime,
        reporttime=arrow.utcnow().datetime
    )


@pytest.yield_fixture
def token(store):
    t = store.store.tokens.create({
        'username': u'test_admin',
        'groups': [u'everyone'],
        'read': u'1',
        'write': u'1',
        'admin': u'1'
    })

    assert t
    yield t['token']
