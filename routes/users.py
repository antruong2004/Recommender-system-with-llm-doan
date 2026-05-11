from flask import Blueprint, jsonify, request


def create_users_blueprint(services):
    product_manager = services['product_manager']
    ai_recommender = services['ai_recommender']
    fmt_product = services['fmt_product']

    bp = Blueprint('users_api', __name__)

    @bp.route('/api/users', methods=['GET'])
    def get_users():
        return jsonify({'users': product_manager.users})

    @bp.route('/api/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        user = product_manager.get_user_profile(user_id)
        if not user:
            return jsonify({'error': 'Khong tim thay nguoi dung'}), 404
        orders = product_manager.get_user_orders(user_id)

        if ai_recommender:
            try:
                items = ai_recommender.hybrid_recommend(user_id=user_id, top_k=4)
                recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                recs = [p for p in recs if p]
            except Exception:
                recs = product_manager.get_hybrid_recommendations(user_id=user_id, n=4)
        else:
            recs = product_manager.get_hybrid_recommendations(user_id=user_id, n=4)

        cluster_info = ai_recommender.get_user_cluster(user_id) if ai_recommender else None
        return jsonify(
            {
                'user': user,
                'orders': orders,
                'recommendations': [fmt_product(p, product_manager) for p in recs],
                'cluster_info': cluster_info,
            }
        )

    @bp.route('/api/users/<user_id>/recommendations', methods=['GET'])
    def user_recommendations(user_id):
        n = request.args.get('n', 6, type=int)
        product_id = request.args.get('product_id', type=int)
        method = request.args.get('method', 'hybrid')

        if ai_recommender:
            try:
                if method == 'tfidf' and product_id:
                    items = ai_recommender.tfidf_similar(product_id, n)
                    recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                    recs = [p for p in recs if p]
                    return jsonify({'recommendations': [fmt_product(p, product_manager) for p in recs], 'method': method})
                if method == 'item_cf' and product_id:
                    items = ai_recommender.item_cf_similar(product_id, n)
                    recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                    recs = [p for p in recs if p]
                    return jsonify({'recommendations': [fmt_product(p, product_manager) for p in recs], 'method': method})
                if method == 'svd':
                    items = ai_recommender.svd_recommend(user_id, n)
                    recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                    recs = [p for p in recs if p]
                    return jsonify({'recommendations': [fmt_product(p, product_manager) for p in recs], 'method': method})
                if method == 'cluster':
                    items = ai_recommender.cluster_recommend(user_id, n)
                    recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                    recs = [p for p in recs if p]
                    cluster_info = ai_recommender.get_user_cluster(user_id)
                    return jsonify(
                        {
                            'recommendations': [fmt_product(p, product_manager) for p in recs],
                            'method': method,
                            'cluster_info': cluster_info,
                        }
                    )
                if method == 'popularity':
                    category = request.args.get('category')
                    items = ai_recommender.popularity_top(n, category=category)
                    recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                    recs = [p for p in recs if p]
                    return jsonify({'recommendations': [fmt_product(p, product_manager) for p in recs], 'method': method})
                if method == 'trending':
                    items = ai_recommender.trending_top(n)
                    recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                    recs = [p for p in recs if p]
                    return jsonify({'recommendations': [fmt_product(p, product_manager) for p in recs], 'method': method})

                items = ai_recommender.hybrid_recommend(user_id=user_id, product_id=product_id, top_k=n)
                recs = [product_manager.get_product_by_id(x['product_id']) for x in items]
                recs = [p for p in recs if p]
                return jsonify({'recommendations': [fmt_product(p, product_manager) for p in recs], 'method': 'ai_hybrid'})
            except Exception as exc:
                print(f"  [AI rec] fallback due to: {exc}")

        if method == 'cbf' and product_id:
            recs = product_manager.get_content_based_recommendations(product_id, n)
        elif method == 'cf':
            recs = product_manager.get_collaborative_recommendations(user_id, n)
        else:
            recs = product_manager.get_hybrid_recommendations(user_id, product_id, n)

        return jsonify({'recommendations': [fmt_product(p, product_manager) for p in recs], 'method': method})

    return bp
