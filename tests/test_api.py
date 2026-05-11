def test_stats_endpoint_returns_summary(client):
    response = client.get('/api/stats')
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['total_products'] > 0
    assert payload['total_users'] > 0
    assert payload['total_orders'] > 0
    assert isinstance(payload['categories'], dict)


def test_products_endpoint_supports_pagination(client):
    response = client.get('/api/products?page=1&per_page=5')
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['page'] == 1
    assert payload['per_page'] == 5
    assert payload['total'] >= len(payload['products'])
    assert len(payload['products']) <= 5


def test_chat_requires_non_empty_message(client):
    response = client.post('/api/chat', json={'message': '   '})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_search_requires_query(client):
    response = client.get('/api/products/search?q=')
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_db_counts_endpoint_returns_counts(client):
    response = client.get('/api/db/counts')
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['source'] in {'db', 'memory'}
    assert 'counts' in payload
    assert payload['counts']['products'] > 0
    assert payload['counts']['users'] > 0
    assert 'orders' in payload['counts']


def test_ai_health_endpoint_returns_component_status(client):
    response = client.get('/api/ai/health')
    assert response.status_code == 200

    payload = response.get_json()
    assert 'ready' in payload
    assert 'components' in payload
    assert 'recommender' in payload['components']
    assert 'vector_search' in payload['components']
    assert 'data' in payload
    assert payload['data']['source'] in {'db', 'memory'}
