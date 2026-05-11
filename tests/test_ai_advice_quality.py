import pytest


def _normalize_text(value: str) -> str:
    return (value or '').strip().lower()


@pytest.fixture()
def client_with_stubbed_llm(client, monkeypatch):
    import core.ecommerce_core as ecommerce_core

    def fake_call_groq_with_retry(system_prompt, messages, max_retries=3, return_model=False):
        response = "Minh da phan tich nhu cau va de xuat cac san pham phu hop."
        if return_model:
            return response, 'stub-llm'
        return response

    monkeypatch.setattr(ecommerce_core, 'call_groq_with_retry', fake_call_groq_with_retry)
    return client


def test_ai_advice_keeps_brand_constraint(client_with_stubbed_llm):
    products_resp = client_with_stubbed_llm.get('/api/products?page=1&per_page=20')
    assert products_resp.status_code == 200
    sample_products = products_resp.get_json()['products']
    existing_brand = sample_products[0]['brand']

    response = client_with_stubbed_llm.post(
        '/api/chat',
        json={'message': f'Toi muon mua san pham thuong hieu {existing_brand}', 'session_id': 'brand-check'},
    )
    assert response.status_code == 200

    payload = response.get_json()
    products = payload['relevant_products']

    assert payload['model_used'] == 'stub-llm'
    assert all(_normalize_text(p.get('brand')) == _normalize_text(existing_brand) for p in products)


def test_ai_advice_keeps_category_constraint(client_with_stubbed_llm):
    response = client_with_stubbed_llm.post(
        '/api/chat',
        json={'message': 'Tu van laptop cho minh', 'session_id': 'category-check'},
    )
    assert response.status_code == 200

    payload = response.get_json()
    products = payload['relevant_products']

    assert len(products) > 0
    assert all(_normalize_text(p.get('category')) == 'laptop' for p in products)


def test_ai_advice_returns_structured_recommendation_products(client_with_stubbed_llm):
    response = client_with_stubbed_llm.post(
        '/api/chat',
        json={'message': 'Goi y san pham cong nghe cho sinh vien', 'session_id': 'structure-check'},
    )
    assert response.status_code == 200

    payload = response.get_json()
    products = payload['relevant_products']

    assert len(products) > 0
    required_keys = {
        'id',
        'name',
        'price',
        'original_price',
        'price_formatted',
        'original_price_formatted',
        'rating',
        'reviews',
        'category',
        'brand',
        'discount',
        'stock',
        'tags',
        'description',
    }

    for item in products:
        assert required_keys.issubset(item.keys())
        assert item['price'] > 0
        assert 1.0 <= float(item['rating']) <= 5.0