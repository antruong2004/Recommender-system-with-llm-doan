from time import perf_counter

from flask import Blueprint, jsonify


def create_analytics_blueprint(services):
    product_manager = services['product_manager']
    db_service = services.get('db_service')
    vector_engine = services.get('vector_engine')
    ai_recommender = services.get('ai_recommender')

    bp = Blueprint('analytics_api', __name__)

    @bp.route('/api/analytics', methods=['GET'])
    def analytics():
        data = product_manager.get_analytics()
        return jsonify(data)

    @bp.route('/api/stats', methods=['GET'])
    def get_stats():
        products = product_manager.get_all_products()
        categories = {}
        for p in products:
            cat = p['category']
            categories[cat] = categories.get(cat, 0) + 1
        return jsonify(
            {
                'total_products': len(products),
                'total_users': len(product_manager.users),
                'total_orders': len(product_manager.orders),
                'categories': categories,
                'avg_rating': round(sum(p['rating'] for p in products) / len(products), 2),
            }
        )

    @bp.route('/api/metadata', methods=['GET'])
    def get_metadata():
        products = product_manager.get_all_products()
        return jsonify(
            {
                'categories': sorted(list(set(p['category'] for p in products))),
                'brands': sorted(list(set(p['brand'] for p in products))),
                'price_range': {
                    'min': min(p['price'] for p in products),
                    'max': max(p['price'] for p in products),
                },
            }
        )

    @bp.route('/api/db/counts', methods=['GET'])
    def get_db_counts():
        if db_service:
            try:
                counts = db_service.get_table_counts()
                return jsonify({'source': 'db', 'counts': counts})
            except Exception as exc:
                print(f"  [DB] Khong the doc counts: {exc}")

        counts = {
            'products': len(product_manager.products),
            'users': len(product_manager.users),
            'orders': len(product_manager.orders),
            'reviews': 0,
            'behavior_logs': 0,
            'chat_messages': 0,
        }
        return jsonify({'source': 'memory', 'counts': counts})

    @bp.route('/api/ai/health', methods=['GET'])
    def get_ai_health():
        recommender_check_ms = None
        recommender_ready = ai_recommender is not None
        recommender_models = []
        recommender_error = None

        if ai_recommender is not None:
            t0 = perf_counter()
            try:
                model_info = ai_recommender.model_info()
                recommender_models = sorted(list(model_info.keys()))
            except Exception as exc:
                recommender_ready = False
                recommender_error = str(exc)
            recommender_check_ms = round((perf_counter() - t0) * 1000, 2)

        vector_check_ms = None
        vector_ready = False
        vector_size = 0
        vector_model = None

        if vector_engine is not None:
            t1 = perf_counter()
            try:
                vector_ready = bool(getattr(vector_engine, 'is_available', False))
                vector_size = len(getattr(vector_engine, 'vectors', []) or [])
                vector_model = getattr(vector_engine, 'model_name', None)
            except Exception:
                vector_ready = False
            vector_check_ms = round((perf_counter() - t1) * 1000, 2)

        if db_service:
            try:
                counts = db_service.get_table_counts(['products', 'users', 'orders', 'reviews', 'behavior_logs'])
                data_source = 'db'
            except Exception:
                counts = {
                    'products': len(product_manager.products),
                    'users': len(product_manager.users),
                    'orders': len(product_manager.orders),
                    'reviews': 0,
                    'behavior_logs': 0,
                }
                data_source = 'memory'
        else:
            counts = {
                'products': len(product_manager.products),
                'users': len(product_manager.users),
                'orders': len(product_manager.orders),
                'reviews': 0,
                'behavior_logs': 0,
            }
            data_source = 'memory'

        overall_ready = recommender_ready and vector_ready
        return jsonify(
            {
                'ready': overall_ready,
                'components': {
                    'recommender': {
                        'ready': recommender_ready,
                        'models': recommender_models,
                        'check_ms': recommender_check_ms,
                        'error': recommender_error,
                    },
                    'vector_search': {
                        'ready': vector_ready,
                        'vectors': vector_size,
                        'model': vector_model,
                        'check_ms': vector_check_ms,
                    },
                },
                'data': {
                    'source': data_source,
                    'counts': counts,
                },
            }
        )

    return bp
