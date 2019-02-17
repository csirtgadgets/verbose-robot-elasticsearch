
import arrow
from pprint import pprint
import pytest

from . import store, indicator, token


def test_indicators_create(store, token, indicator):
    store.handle_indicators_create(token, [indicator], flush=True, force=True)

    x = store.handle_indicators_search(token, {
        'indicator': indicator['indicator'],
    })
    assert len(x) == 1


def test_indicators_search_fqdn(store, token, indicator):
    indicator['indicator'] = 'example.com'
    store.handle_indicators_create(token, [indicator], flush=True, force=True)

    x = store.handle_indicators_search(token, {
        'indicator': 'example.com',
    })

    assert len(x) == 1

    indicator['tags'] = 'botnet'
    indicator['indicator'] = 'example2.com'

    store.handle_indicators_create(token, indicator, flush=True, force=True)

    x = store.handle_indicators_search(token, {
        'indicator': 'example2.com',
    })

    assert len(x) == 1

    x = store.handle_indicators_search(token, {
        'indicator': 'example2.com',
        'tags': 'malware'
    })

    assert len(x) == 0


def test_indicators_search_ipv4(store, token, indicator):
    indicator['indicator'] = '192.168.1.1'
    indicator['itype'] = 'ipv4'
    indicator['tags'] = 'botnet'

    store.handle_indicators_create(token, indicator, flush=True, force=True)

    for i in ['192.168.1.1', '192.168.1.0/24']:
        x = store.handle_indicators_search(token, {
            'indicator': i,
        })

        assert len(x) > 0


@pytest.mark.xfail(reason='Need to re-look at v6 handling..')
def test_indicators_search_ipv6(store, token, indicator):
    indicator['indicator'] = '2001:4860:4860::8888'
    indicator['itype'] = 'ipv6'
    indicator['tags'] = 'botnet'

    store.handle_indicators_create(token, indicator, flush=True, force=True)

    x = store.handle_indicators_search(token, {
        'indicator': '2001:4860:4860::8888',
    })

    assert len(x) > 0

    x = store.handle_indicators_search(token, {
        'indicator': '2001:4860::/32',
    })

    assert len(x) > 0


@pytest.mark.xfail(reason='not yet implemented..')
def test_indicators_delete(store, token, indicator):
    store.handle_indicators_create(token, indicator, flush=True, force=True)

    r = store.handle_indicators_delete(token, data=[{
        'indicator': 'example.com',
    }])
    assert r == 1

    x = store.handle_indicators_search(token, {
        'indicator': 'example.com',
        'nolog': 1
    })
    assert len(x) == 0

    x = store.handle_indicators_search(token, {
        'indicator': 'example2.com',
        'nolog': 1
    })

    for xx in x:
        r = store.handle_indicators_delete(token, data=[{
            'id': xx['id']
        }])
        assert r == 1


def test_indicators_create_sha1(store, token, indicator):
    t = store.store.tokens.admin_exists()

    indicator['indicator'] = 'd52380918a07322c50f1bfa2b43af3bb54cb33db'
    indicator['group'] = 'everyone'
    indicator['itype'] = 'sha1'

    store.handle_indicators_create(token, indicator, flush=True, force=True)

    x = store.handle_indicators_search(token, {
        'indicator': 'd52380918a07322c50f1bfa2b43af3bb54cb33db',
        'nolog': 1
    })

    assert len(x) > 0
