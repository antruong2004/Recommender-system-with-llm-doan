import math

from flask import Blueprint, jsonify, request


def create_products_blueprint(services):
    product_manager = services['product_manager']
    vector_engine = services['vector_engine']
    ai_recommender = services['ai_recommender']
    fmt_product = services['fmt_product']
    call_groq_with_retry = services['call_groq_with_retry']

    bp = Blueprint('products_api', __name__)

    @bp.route('/api/products', methods=['GET'])
    def get_products():
        category = request.args.get('category')
        brand = request.args.get('brand')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        tags_raw = request.args.get('tags')
        tags = tags_raw.split(',') if tags_raw else None
        sort_by = request.args.get('sort_by')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)

        products = product_manager.filter_products(
            category=category,
            brand=brand,
            min_price=int(min_price) if min_price else None,
            max_price=int(max_price) if max_price else None,
            tags=tags,
            sort_by=sort_by,
        )
        total = len(products)
        start = (page - 1) * per_page
        paginated = products[start:start + per_page]

        return jsonify(
            {
                'products': [fmt_product(p, product_manager) for p in paginated],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': math.ceil(total / per_page),
            }
        )

    @bp.route('/api/products/search', methods=['GET'])
    def search_products():
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Vui long nhap tu khoa'}), 400
        results = product_manager.search_products(query)
        return jsonify(
            {
                'results': [fmt_product(p, product_manager) for p in results],
                'total': len(results),
                'query': query,
            }
        )

    @bp.route('/api/products/semantic-search', methods=['GET'])
    def semantic_search_products():
        query = request.args.get('q', '').strip()
        top_k = request.args.get('top_k', 6, type=int)
        min_sim = request.args.get('min_sim', 0.10, type=float)
        if not query:
            return jsonify({'error': 'Vui long nhap tu khoa'}), 400

        if not vector_engine.is_available:
            kw_results = product_manager.search_products(query)[:top_k]
            return jsonify(
                {
                    'results': [fmt_product(p, product_manager) for p in kw_results],
                    'total': len(kw_results),
                    'query': query,
                    'method': 'keyword_fallback',
                }
            )

        vec_results = vector_engine.semantic_search(query, top_k=top_k, min_sim=min_sim)
        out = []
        for vr in vec_results:
            p = product_manager.get_product_by_id(vr['product_id'])
            if p:
                fp = fmt_product(p, product_manager)
                fp['similarity_score'] = round(vr['similarity'], 4)
                out.append(fp)

        return jsonify(
            {
                'results': out,
                'total': len(out),
                'query': query,
                'method': 'vector_cosine',
                'model': vector_engine.meta.get('model', ''),
                'dimension': vector_engine.meta.get('dimension', 0),
            }
        )

    @bp.route('/api/products/top', methods=['GET'])
    def top_products():
        category = request.args.get('category')
        n = request.args.get('n', 6, type=int)
        products = product_manager.get_top_products(n=n, category=category)
        return jsonify({'products': [fmt_product(p, product_manager) for p in products]})

    @bp.route('/api/products/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        product = product_manager.get_product_by_id(product_id)
        if not product:
            return jsonify({'error': 'Khong tim thay san pham'}), 404
        reviews = product_manager.get_product_reviews(product_id)

        if ai_recommender:
            try:
                hybrid_ids = ai_recommender.hybrid_recommend(product_id=product_id, top_k=6)
                recommendations = [product_manager.get_product_by_id(x['product_id']) for x in hybrid_ids]
                recommendations = [p for p in recommendations if p]
            except Exception:
                recommendations = product_manager.get_content_based_recommendations(product_id, n=4)
        else:
            recommendations = product_manager.get_content_based_recommendations(product_id, n=4)

        return jsonify(
            {
                'product': product,
                'reviews': reviews,
                'recommendations': [fmt_product(p, product_manager) for p in recommendations],
            }
        )

    @bp.route('/api/products/compare', methods=['POST'])
    def compare_products():
        data = request.json or {}
        product_ids = data.get('product_ids', [])
        if len(product_ids) < 2:
            return jsonify({'error': 'Can it nhat 2 san pham de so sanh'}), 400

        products = [product_manager.get_product_by_id(pid) for pid in product_ids]
        products = [p for p in products if p]
        if len(products) < 2:
            return jsonify({'error': 'Khong tim thay san pham'}), 404

        product_texts = '\n\n'.join([product_manager.product_to_text(p) for p in products])
        system = """Ban la chuyen gia phan tich san pham cong nghe. 
Hay so sanh chi tiet cac san pham duoc cung cap va dua ra khuyen nghi cuoi cung.
Tra loi bang tieng Viet, su dung bang so sanh ro rang, neu ro uu nhuoc diem tung san pham."""

        messages = [
            {
                'role': 'user',
                'content': f"So sanh chi tiet cac san pham sau va cho biet nen mua cai nao:\n\n{product_texts}",
            }
        ]
        try:
            comparison = call_groq_with_retry(system, messages)
        except Exception as e:
            comparison = f"Khong the so sanh do loi: {str(e)[:100]}"

        return jsonify(
            {
                'comparison': comparison,
                'products': [fmt_product(p, product_manager) for p in products],
            }
        )

    @bp.route('/api/products/trending', methods=['GET'])
    def trending_products():
        n = request.args.get('n', 10, type=int)
        if not ai_recommender:
            return jsonify({'error': 'AI recommender chua san sang'}), 503
        items = ai_recommender.trending_top(n)
        recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
        out = []
        for p, item in zip(recs, items):
            if p:
                fp = fmt_product(p, product_manager)
                fp['trend_ratio'] = item['score']
                out.append(fp)
        return jsonify({'products': out, 'total': len(out)})

    @bp.route('/api/recommend', methods=['GET'])
    def flexible_recommend():
        method = request.args.get('method', 'hybrid')
        user_id = request.args.get('user_id')
        product_id = request.args.get('product_id', type=int)
        n = request.args.get('n', 8, type=int)
        category = request.args.get('category')

        if not ai_recommender and method not in ('semantic', 'keyword'):
            return jsonify({'error': 'AI recommender chua san sang'}), 503

        try:
            if method == 'tfidf':
                if not product_id:
                    return jsonify({'error': 'Can product_id'}), 400
                items = ai_recommender.tfidf_similar(product_id, n)
            elif method == 'item_cf':
                if not product_id:
                    return jsonify({'error': 'Can product_id'}), 400
                items = ai_recommender.item_cf_similar(product_id, n)
            elif method == 'svd':
                if not user_id:
                    return jsonify({'error': 'Can user_id'}), 400
                items = ai_recommender.svd_recommend(user_id, n)
            elif method == 'cluster':
                if not user_id:
                    return jsonify({'error': 'Can user_id'}), 400
                items = ai_recommender.cluster_recommend(user_id, n)
            elif method == 'popularity':
                items = ai_recommender.popularity_top(n, category=category)
            elif method == 'trending':
                items = ai_recommender.trending_top(n)
            elif method == 'semantic':
                q = request.args.get('q', '')
                if not q:
                    return jsonify({'error': 'Can q=...'}), 400
                vec_results = vector_engine.semantic_search(q, top_k=n)
                items = [{'product_id': r['product_id'], 'score': r['similarity']} for r in vec_results]
            else:
                items = ai_recommender.hybrid_recommend(
                    user_id=user_id,
                    product_id=product_id,
                    category=category,
                    top_k=n,
                )

            pids = [x['product_id'] for x in items]
            scores = {x['product_id']: x.get('score', x.get('hybrid_score', 0)) for x in items}
            products = [product_manager.get_product_by_id(pid) for pid in pids]
            out = []
            for p in products:
                if p:
                    fp = fmt_product(p, product_manager)
                    fp['ai_score'] = round(float(scores.get(p['id'], 0)), 4)
                    out.append(fp)

            extra = {}
            if user_id and method == 'cluster' and ai_recommender:
                extra['cluster_info'] = ai_recommender.get_user_cluster(user_id)

            return jsonify({'recommendations': out, 'method': method, 'total': len(out), **extra})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @bp.route('/api/models', methods=['GET'])
    def models_info():
        vec_info = {
            'available': vector_engine.is_available,
            'n_vectors': len(vector_engine.vectors) if vector_engine.is_available else 0,
            'dimension': vector_engine.meta.get('dimension', 0),
            'model': vector_engine.meta.get('model', ''),
        }
        ml_info = ai_recommender.model_info() if ai_recommender else {}
        return jsonify({'semantic_search': vec_info, 'ml_models': ml_info, 'total_models': 1 + len(ml_info)})

    return bp
