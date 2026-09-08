import json

from fastapi.testclient import TestClient

from ghost_talent import app as app_module


client = TestClient(app_module.app)


def test_preview_is_explicitly_disabled():
    response = client.get('/api/scout/preview', params={'q': 'cuda triton'})
    assert response.status_code == 409
    detail = response.json()['detail']
    assert detail['code'] == 'preview_disabled'
    assert detail['complete'] is False
    assert detail['snapshot_written'] is False


def test_watchlist_accepts_top_level_login_then_deletes(tmp_path, monkeypatch):
    watchlist = tmp_path / 'watchlist.json'
    monkeypatch.setattr(app_module, 'WATCHLIST_PATH', watchlist)

    put = client.put('/api/watchlist/Alice', json={'login': 'Alice', 'radar_score': 42})
    assert put.status_code == 200
    assert put.json()['item']['candidate']['login'] == 'Alice'
    assert 'login' not in put.json()['item']

    saved = json.loads(watchlist.read_text(encoding='utf-8'))
    assert saved['items'][0]['candidate']['login'] == 'Alice'

    delete = client.delete('/api/watchlist/alice')
    assert delete.status_code == 200
    assert delete.json()['removed'] is True
    assert delete.json()['count'] == 0

    get = client.get('/api/watchlist')
    assert get.status_code == 200
    assert get.json() == {'count': 0, 'items': []}


def test_watchlist_put_is_case_insensitive_and_deduplicates(tmp_path, monkeypatch):
    watchlist = tmp_path / 'watchlist.json'
    monkeypatch.setattr(app_module, 'WATCHLIST_PATH', watchlist)

    assert client.put('/api/watchlist/Alice', json={'candidate': {'login': 'Alice'}, 'radar_score': 10}).status_code == 200
    second = client.put('/api/watchlist/alice', json={'candidate': {'login': 'alice'}, 'radar_score': 20})
    assert second.status_code == 200
    assert second.json()['count'] == 1

    get = client.get('/api/watchlist').json()
    assert get['count'] == 1
    assert get['items'][0]['radar_score'] == 20
