# ============================================================
# TECHSTORE AI - APP.PY OPTIMIZED VERSION
# ============================================================

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from core.db_service import DBService
from core.ecommerce_core import (
    GROQ_API_KEY,
    EcommerceAdvisor,
    ProductManager,
    VectorSearchEngine,
    _fmt_product,
    call_groq_with_retry,
)
from routes import register_routes

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

try:
    from recommender import get_recommender as _get_recommender

    _RECOMMENDER_AVAILABLE = True
except Exception as exc:
    _RECOMMENDER_AVAILABLE = False
    logger.warning('Cannot import recommender: %s', exc)
    _get_recommender = None

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'techstore-secret-2026')
CORS(app, resources={r'/api/*': {'origins': '*'}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKIP_VECTORS = os.getenv('SKIP_VECTORS', '0').strip().lower() in ('1', 'true', 'yes')
SKIP_RECOMMENDER = os.getenv('SKIP_RECOMMENDER', '0').strip().lower() in ('1', 'true', 'yes')
SKIP_DB = os.getenv('SKIP_DB', '0').strip().lower() in ('1', 'true', 'yes')

logger.info('Loading ProductManager...')
product_manager = ProductManager(base_dir=BASE_DIR)
logger.info('Products loaded: %s', len(product_manager.products))

vector_engine = None
if not SKIP_VECTORS:
    try:
        vector_path = os.path.join(BASE_DIR, 'data', 'product_vectors.json')
        vector_engine = VectorSearchEngine(vector_path)
        logger.info('Vector engine ready')
    except Exception as exc:
        logger.error('Cannot load vector engine: %s', exc)
        vector_engine = None
else:
    logger.warning('SKIP_VECTORS enabled')

ai_recommender = None
if _RECOMMENDER_AVAILABLE and not SKIP_RECOMMENDER:
    try:
        ai_recommender = _get_recommender()
        model_info = ai_recommender.model_info()
        logger.info('Recommender ready: %s', list(model_info.keys()))
    except Exception as exc:
        logger.error('Cannot load recommender: %s', exc)
        ai_recommender = None
else:
    logger.warning('Recommender skipped')

advisor = EcommerceAdvisor(
    product_manager=product_manager,
    vector_engine=vector_engine,
    ai_recommender=ai_recommender,
)
logger.info('Advisor initialized')

db_service = None
if not SKIP_DB:
    try:
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/shop')
        db_service = DBService(database_url)
        logger.info('PostgreSQL connected')
    except Exception as exc:
        logger.error('Database connection failed: %s', exc)
        db_service = None
else:
    logger.warning('Database skipped')

services = {
    'product_manager': product_manager,
    'vector_engine': vector_engine,
    'ai_recommender': ai_recommender,
    'advisor': advisor,
    'db_service': db_service,
    'fmt_product': _fmt_product,
    'call_groq_with_retry': call_groq_with_retry,
}
register_routes(app, services)
logger.info('Routes registered')


@app.get('/health')
def health_check():
    return jsonify(
        {
            'status': 'ok',
            'products': len(product_manager.products),
            'users': len(product_manager.users),
            'orders': len(product_manager.orders),
            'vector_enabled': bool(vector_engine and vector_engine.is_available),
            'recommender_enabled': ai_recommender is not None,
            'db_enabled': db_service is not None,
        }
    )


@app.get('/api/debug/runtime')
def debug_runtime():
    top_trending = product_manager.get_trending_products(n=5)
    trending_ids = [p.get('id') for p in top_trending]
    recommender_ids = []
    recommender_error = None
    if ai_recommender:
        try:
            recommender_ids = [x.get('product_id') for x in ai_recommender.trending_top(top_k=5)]
        except Exception as exc:
            recommender_error = str(exc)
    return jsonify(
        {
            'status': 'ok',
            'runtime': {
                'pid': os.getpid(),
                'base_dir': BASE_DIR,
                'products': len(product_manager.products),
                'users': len(product_manager.users),
                'orders': len(product_manager.orders),
                'vector_enabled': bool(vector_engine and vector_engine.is_available),
                'recommender_enabled': ai_recommender is not None,
                'db_enabled': db_service is not None,
            },
            'sources': {
                'api_products_trending': {
                    'source': 'recommender.m5_popularity' if ai_recommender else ('postgresql' if db_service else 'json'),
                    'answer_source': 'recommender.m5_popularity' if ai_recommender else 'api.products.trending',
                    'top_ids': recommender_ids if recommender_ids else trending_ids,
                    'recommender_error': recommender_error,
                },
                'product_manager_trending': {
                    'top_ids': trending_ids,
                },
            },
        }
    )


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0').strip().lower() in ('1', 'true', 'yes')
    use_reloader = os.getenv('FLASK_RELOADER', '0').strip().lower() in ('1', 'true', 'yes')
    port = int(os.getenv('PORT', '5000'))

    print('=' * 60)
    print(' TECHSTORE AI - ECOMMERCE ADVISOR')
    print('=' * 60)
    print(f'Products     : {len(product_manager.products)}')
    print(f'Users        : {len(product_manager.users)}')
    print(f'Orders       : {len(product_manager.orders)}')
    print(f"Vectors      : {'READY' if vector_engine and vector_engine.is_available else 'DISABLED'}")
    print(f"Recommender  : {'READY' if ai_recommender else 'DISABLED'}")
    print(f"Database     : {'READY' if db_service else 'DISABLED'}")
    print(f'Server       : http://localhost:{port}')
    print(f'Dashboard    : http://localhost:{port}/dashboard')
    print(f'Health       : http://localhost:{port}/health')
    print('=' * 60)

    if not GROQ_API_KEY:
        logger.warning('GROQ_API_KEY missing')

    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=use_reloader, threaded=True)
