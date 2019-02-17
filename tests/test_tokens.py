
import pytest
from datetime import datetime

from . import store


def test_tokens(store):
    t = store.store.tokens.admin_exists()
    assert t

    t = list(store.store.tokens.search({'token': t}))
    assert len(t) > 0

    t = t[0]['token']

    assert store.store.tokens.update_last_activity_at(t, datetime.now())
    assert store.store.tokens.check(t, 'read')
    assert store.store.tokens.read(t)
    assert store.store.tokens.write(t)
    assert store.store.tokens.admin(t)
    assert store.store.tokens.last_activity_at(t) is not None
    assert store.store.tokens.update_last_activity_at(t, datetime.now())
