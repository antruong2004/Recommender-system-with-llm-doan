from __future__ import annotations

from flask import jsonify, render_template, request


def register_routes(app, services):
    pm = services['product_manager']
    vector_engine = services.get('vector_engine')
    ai_recommender = services.get('ai_recommender')
    advisor = services['advisor']
    db_service = services.get('db_service')
    fmt_product = services['fmt_product']

    def _json_error(message, status=400, **extra):
        payload = {'error': message}
        payload.update(extra)
        return jsonify(payload), status

    def _get_int_arg(name, default, min_value=None, max_value=None):
        try:
            value = int(request.args.get(name, default))
        except (TypeError, ValueError):
            value = default
        if min_value is not None:
            value = max(min_value, value)
        if max_value is not None:
            value = min(max_value, value)
        return value

    def _format_recommendations(products):
        return [fmt_product(p, pm) for p in products]

    def _make_trace(sources=None, **extra):
        trace = {
            'sources': sources or [],
            'retrieved_count': 0,
            'retrieved_products': [],
            'returned_count': 0,
            'requested_brand': None,
            'requested_categories': [],
            'has_user_context': False,
            'has_rec_context': False,
            'is_first_turn': False,
        }
        trace.update(extra)
        return trace

    def _top_products_from_trending(top_n: int):
        top_items = pm.get_trending_products(n=top_n)
        trend_source = 'postgresql' if db_service else 'json'
        if top_items:
            for item in top_items:
                item['trend_source'] = trend_source
            return top_items, trend_source

        orders = db_service.get_orders() if db_service else pm.orders
        product_order_count = {}
        for order in orders:
            pid = order.get('product_id')
            if pid is None:
                continue
            product_order_count[pid] = product_order_count.get(pid, 0) + 1

        fallback_items = []
        for pid, count in sorted(product_order_count.items(), key=lambda item: item[1], reverse=True)[:top_n]:
            product = pm.get_product_by_id(pid)
            if not product:
                continue
            item = dict(product)
            item['trend_count'] = count
            item['trend_ratio'] = count / max(1, len(orders))
            item['trend_source'] = trend_source
            fallback_items.append(item)
        return fallback_items, trend_source

    @app.get('/')
    def index():
        return render_template('dashboard.html')

    @app.get('/index')
    def index_page():
        return render_template('dashboard.html')

    @app.get('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.get('/api/health')
    def health():
        vec_ready = bool(vector_engine and getattr(vector_engine, 'is_available', False))
        rec_ready = bool(ai_recommender)
        db_ready = bool(db_service)
        return jsonify(
            {
                'ready': True,
                'source': 'system',
                'trace': _make_trace(['vector_search', 'recommender', 'database']),
                'components': {
                    'vector_search': {
                        'ready': vec_ready,
                        'vectors': len(getattr(vector_engine, 'vectors', []) or []),
                    },
                    'recommender': {
                        'ready': rec_ready,
                        'models': list(ai_recommender.model_info().keys()) if rec_ready else [],
                    },
                    'database': {'ready': db_ready},
                },
            }
        )

    @app.get('/api/ai/health')
    def ai_health():
        vec_ready = bool(vector_engine and getattr(vector_engine, 'is_available', False))
        rec_ready = bool(ai_recommender)
        return jsonify(
            {
                'ready': vec_ready or rec_ready,
                'source': 'system',
                'trace': _make_trace(['vector_search', 'recommender', 'database']),
                'components': {
                    'vector_search': {
                        'ready': vec_ready,
                        'vectors': len(getattr(vector_engine, 'vectors', []) or []),
                        'check_ms': 0,
                    },
                    'recommender': {
                        'ready': rec_ready,
                        'models': list(ai_recommender.model_info().keys()) if rec_ready else [],
                        'check_ms': 0,
                    },
                },
                'data': {
                    'source': 'postgresql' if db_service else 'json',
                    'counts': db_service.get_table_counts() if db_service else {
                        'products': len(pm.products),
                        'users': len(pm.users),
                        'orders': len(pm.orders),
                    },
                },
            }
        )

    @app.get('/api/db/counts')
    def db_counts():
        if db_service:
            return jsonify({'source': 'postgresql', 'counts': db_service.get_table_counts(), 'trace': _make_trace(['chat_messages', 'orders', 'products', 'users', 'reviews', 'behavior_logs'])})
        return jsonify({'source': 'json', 'counts': {'products': len(pm.products), 'users': len(pm.users), 'orders': len(pm.orders), 'reviews': 0, 'behavior_logs': 0, 'chat_messages': 0}, 'trace': _make_trace(['products.json', 'users.json', 'orders.json'])})

    @app.get('/api/models')
    def models():
        model_info = ai_recommender.model_info() if ai_recommender else {}
        return jsonify({'total_models': len(model_info), 'models': model_info, 'source': 'recommender', 'trace': _make_trace(['recommender'])})

    @app.get('/api/stats')
    def stats():
        data = pm.get_analytics()
        category_counts = {}
        for p in pm.products:
            category_counts[p['category']] = category_counts.get(p['category'], 0) + 1
        data['categories'] = category_counts
        data['source'] = 'products_json'
        data['trace'] = _make_trace(['products.json', 'orders.json'])
        return jsonify(data)

    @app.get('/api/products')
    def products():
        category = request.args.get('category')
        brand = request.args.get('brand')
        sort_by = request.args.get('sort_by')
        tags = request.args.get('tags')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        results = pm.filter_products(
            category=category,
            brand=brand,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None,
            tags=[t.strip() for t in tags.split(',')] if tags else None,
            sort_by=sort_by,
        )
        return jsonify({'products': _format_recommendations(results), 'source': 'products_json', 'answer_source': 'products_json', 'trace': _make_trace(['products.json'], returned_count=len(results))})

    @app.get('/api/products/<int:product_id>')
    def product_detail(product_id):
        product = pm.get_product_by_id(product_id)
        if not product:
            return _json_error('Product not found', 404)
        return jsonify({'product': fmt_product(product, pm), 'source': 'products_json', 'answer_source': 'products_json', 'trace': _make_trace(['products.json'])})

    @app.get('/api/products/search')
    def product_search():
        q = request.args.get('q', '').strip()
        if not q:
            return _json_error('Missing q parameter')
        results = pm.search_products(q)
        return jsonify({'query': q, 'products': _format_recommendations(results), 'source': 'products_json', 'answer_source': 'products_json', 'trace': _make_trace(['products.json'], returned_count=len(results))})

    @app.get('/api/products/top')
    def product_top():
        n = _get_int_arg('n', 5, 1, 50)
        category = request.args.get('category')
        results = pm.get_top_products(n=n, category=category)
        return jsonify({'products': _format_recommendations(results), 'source': 'products_json', 'answer_source': 'products_json', 'trace': _make_trace(['products.json'], returned_count=len(results))})

    @app.get('/api/products/trending')
    def product_trending():
        n = _get_int_arg('n', 8, 1, 50)
        source = 'recommender.m5_popularity' if ai_recommender else ('postgresql' if db_service else 'json')
        top_items, trend_source = _top_products_from_trending(n)

        trending = []
        for item in top_items:
            payload = fmt_product(item, pm)
            payload['trend_ratio'] = item.get('trend_ratio', 0)
            payload['trend_count'] = item.get('trend_count', 0)
            payload['source'] = source
            trending.append(payload)

        trace_source = 'recommender.m5_popularity' if ai_recommender else ('db.orders' if db_service else 'json.orders')
        return jsonify({'products': trending, 'source': source, 'answer_source': source if ai_recommender else 'api.products.trending', 'trace': _make_trace([trace_source], returned_count=len(trending), trend_source=trend_source)})

    @app.get('/api/debug/source-check')
    def debug_source_check():
        n = _get_int_arg('n', 5, 1, 10)
        trending_api = product_trending().get_json(silent=True) or {}
        trending_products = trending_api.get('products', []) or []
        top_from_pm = pm.get_trending_products(n=n)
        top_from_orders, orders_source = _top_products_from_trending(n)
        return jsonify({
            'ok': True,
            'meta': {
                'db_enabled': bool(db_service),
                'recommender_enabled': bool(ai_recommender),
                'vector_enabled': bool(vector_engine and getattr(vector_engine, 'is_available', False)),
            },
            'api_products_trending': {
                'source': trending_api.get('source'),
                'answer_source': trending_api.get('answer_source'),
                'trace': trending_api.get('trace', {}),
                'top_ids': [item.get('id') for item in trending_products[:n]],
            },
            'product_manager_trending': {
                'top_ids': [item.get('id') for item in top_from_pm[:n]],
            },
            'orders_trending': {
                'source': orders_source,
                'top_ids': [item.get('id') for item in top_from_orders[:n]],
            },
        })

    @app.get('/api/products/semantic-search')
    def semantic_search():
        q = request.args.get('q', '').strip()
        if not q:
            return _json_error('Missing q parameter')
        top_k = _get_int_arg('top_k', 6, 1, 20)
        if not vector_engine or not vector_engine.is_available:
            return _json_error('Semantic search is not available', 503)
        results = vector_engine.semantic_search(q, top_k=top_k)
        payload = []
        for item in results:
            product = pm.get_product_by_id(item['product_id'])
            if product:
                row = fmt_product(product, pm)
                row['similarity_score'] = item['similarity']
                payload.append(row)
        return jsonify({'query': q, 'results': payload, 'source': 'vector_search', 'answer_source': 'vector_search', 'trace': _make_trace(['product_vectors.json'], returned_count=len(payload))})

    @app.get('/api/recommend')
    def recommend():
        method = (request.args.get('method') or 'hybrid').strip().lower()
        user_id = request.args.get('user_id')
        product_id = request.args.get('product_id')
        category = request.args.get('category')
        top_n = _get_int_arg('n', 6, 1, 30)

        try:
            pid = int(product_id) if product_id else None
            recs = []
            source = 'pm_hybrid'
            trace_sources = []

            if ai_recommender:
                if method == 'hybrid':
                    hybrid = ai_recommender.hybrid_recommend(user_id=user_id, product_id=pid, category=category, top_k=top_n)
                    recs = [pm.get_product_by_id(x['product_id']) for x in hybrid]
                    source = 'recommender.hybrid'
                    trace_sources = ['recommender.hybrid']
                elif method == 'trending':
                    rows = ai_recommender.trending_top(top_k=top_n)
                    recs = [pm.get_product_by_id(x['product_id']) for x in rows]
                    source = 'recommender.m5_popularity'
                    trace_sources = ['recommender.m5_popularity']
                elif method == 'popularity':
                    rows = ai_recommender.popularity_top(top_k=top_n, category=category)
                    recs = [pm.get_product_by_id(x['product_id']) for x in rows]
                    source = 'recommender.popularity'
                    trace_sources = ['recommender.popularity']
                elif method == 'tfidf' and pid:
                    recs = [pm.get_product_by_id(x['product_id']) for x in ai_recommender.tfidf_similar(pid, top_n)]
                    source = 'recommender.tfidf'
                    trace_sources = ['recommender.tfidf']
                elif method == 'item_cf' and pid:
                    recs = [pm.get_product_by_id(x['product_id']) for x in ai_recommender.item_cf_similar(pid, top_n)]
                    source = 'recommender.item_cf'
                    trace_sources = ['recommender.item_cf']
                elif method == 'svd' and user_id:
                    recs = [pm.get_product_by_id(x['product_id']) for x in ai_recommender.svd_recommend(user_id, top_n)]
                    source = 'recommender.svd'
                    trace_sources = ['recommender.svd']
                elif method == 'cluster' and user_id:
                    recs = [pm.get_product_by_id(x['product_id']) for x in ai_recommender.cluster_recommend(user_id, top_n)]
                    source = 'recommender.cluster'
                    trace_sources = ['recommender.cluster']
                else:
                    recs = pm.get_hybrid_recommendations(user_id=user_id, product_id=pid, n=top_n)
                    source = 'pm_hybrid'
                    trace_sources = ['products.json', 'orders.json']
            else:
                recs = pm.get_hybrid_recommendations(user_id=user_id, product_id=pid, n=top_n)
                source = 'pm_hybrid'
                trace_sources = ['products.json', 'orders.json']

            recs = [r for r in recs if r]
            return jsonify({'method': method if ai_recommender else 'pm_hybrid', 'recommendations': _format_recommendations(recs), 'count': len(recs), 'fallback_used': not bool(ai_recommender), 'source': source, 'answer_source': source, 'trace': _make_trace(trace_sources, returned_count=len(recs))})
        except Exception as exc:
            return _json_error(str(exc), 500)

    @app.get('/api/users/<user_id>')
    def user_detail(user_id):
        user = pm.get_user_profile(user_id)
        if not user:
            return _json_error('User not found', 404)
        orders = pm.get_user_orders(user_id)
        return jsonify({'user': user, 'orders': orders, 'source': 'users_json', 'answer_source': 'users_json', 'trace': _make_trace(['users.json', 'orders.json'])})

    @app.get('/api/history/<session_id>')
    def chat_history(session_id):
        if db_service:
            return jsonify({'session_id': session_id, 'messages': db_service.get_chat_history(session_id), 'source': 'postgresql', 'answer_source': 'postgresql', 'trace': _make_trace(['chat_messages'])})
        return jsonify({'session_id': session_id, 'messages': advisor.conversation_histories.get(session_id, []), 'source': 'memory', 'answer_source': 'memory', 'trace': _make_trace(['memory'])})

    @app.delete('/api/history/<session_id>')
    def clear_history(session_id):
        advisor.conversation_histories.pop(session_id, None)
        if db_service:
            db_service.clear_chat_history(session_id)
        return jsonify({'ok': True, 'session_id': session_id, 'source': 'memory+postgresql' if db_service else 'memory', 'answer_source': 'memory+postgresql' if db_service else 'memory', 'trace': _make_trace(['memory', 'chat_messages'])})

    @app.post('/api/chat')
    def chat():
        payload = request.get_json(silent=True) or {}
        message = (payload.get('message') or '').strip()
        if not message:
            return _json_error('message is required')

        session_id = (payload.get('session_id') or 'default').strip()
        user_id = payload.get('user_id')
        normalized = advisor._normalize_text(message)
        is_trending = any(k in normalized for k in ['trending', 'ban chay', 'top san pham', 'thinh hanh', 'quan tam nhat'])

        if is_trending:
            import re
            m = re.search(r'\btop\s*(\d+)\b', normalized)
            top_n = int(m.group(1)) if m else 10
            top_n = max(1, min(top_n, 10))
            top_items, trend_source = _top_products_from_trending(top_n)
            lines = [f'Dưới đây là top {top_n} sản phẩm Trending tại TechStore (lấy từ data thật):', '']
            for idx, p in enumerate(top_items, 1):
                lines.append(
                    f"{idx}. **{p['name']}** - {p['category']} / {p['brand']}\n"
                    f"   - product_id: {p['id']}\n"
                    f"   - Giá: {pm.format_price(p['price'])} (gốc {pm.format_price(p['original_price'])}, giảm {p['discount']}%)\n"
                    f"   - Đánh giá: {p['rating']}/5 ({p['reviews']} đánh giá)\n"
                    f"   - Còn hàng: {p['stock']}\n"
                    f"   - trend_ratio: {p.get('trend_ratio', 0):.4f}"
                )
            response = '\n'.join(lines)
            result = {
                'response': response,
                'relevant_products': [_fmt_product(p, pm) for p in top_items],
                'session_id': session_id,
                'model_used': 'api_trending_hardcoded',
                'recommender_models_used': [],
                'answer_source': 'api.products.trending',
                'source': 'api.products.trending',
                'trace': {
                    'sources': ['api.products.trending', 'db.orders' if db_service else 'json.orders'],
                    'retrieved_count': 0,
                    'retrieved_products': [],
                    'returned_count': len(top_items),
                    'requested_brand': None,
                    'requested_categories': [],
                    'has_user_context': False,
                    'has_rec_context': False,
                    'is_first_turn': True,
                    'trend_source': trend_source,
                },
            }
        else:
            result = advisor.chat(message, session_id=session_id, user_id=user_id)
            result.setdefault('source', 'api.chat.llm')
            result.setdefault('answer_source', 'llm.groq')
            result.setdefault('trace', {})
            result['trace'].setdefault('sources', ['product_retrieval'])

        if db_service:
            db_service.save_chat_message(session_id, 'user', message, user_id=user_id)
            db_service.save_chat_message(session_id, 'assistant', result['response'], user_id=user_id)
            audit = result.get('audit', {}) or {}
            db_service.save_answer_audit(
                session_id,
                message,
                result.get('response', ''),
                user_id=user_id,
                source=result.get('source'),
                model_used=result.get('model_used'),
                answer_source=result.get('answer_source'),
                trace=result.get('trace', {}),
                retrieved_count=int(audit.get('retrieved_count', result.get('trace', {}).get('retrieved_count', 0)) or 0),
                returned_count=int(audit.get('returned_count', result.get('trace', {}).get('returned_count', 0)) or 0),
                confidence=float(result.get('confidence', 0.0) or 0.0) if result.get('confidence') is not None else None,
                is_match=bool(audit.get('matched', False)) if audit else None,
            )

        return jsonify(
            {
                **result,
                'debug': {
                    'trace': result.get('trace', {}),
                    'model_used': result.get('model_used'),
                    'recommender_models_used': result.get('recommender_models_used', []),
                },
            }
        )

    return app
