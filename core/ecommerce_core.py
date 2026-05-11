from __future__ import annotations

import json
import logging
import os
import re
import time
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)
AUDIT_LOG_DIR = Path(os.getenv('AUDIT_LOG_DIR', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')))
AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG_PATH = AUDIT_LOG_DIR / 'ai_audit.log'

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_NAMES = [
    'llama-3.1-8b-instant',
    'llama3-8b-8192',
]

DEFAULT_EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'


def normalize_text(text: str) -> str:
    text = str(text or '').lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    text = re.sub(r'\s+', ' ', text)
    return text


def sanitize_prompt_text(text: str) -> str:
    """Basic prompt-injection sanitization for search/context text."""
    lowered = normalize_text(text)
    dangerous_patterns = ['ignore previous', 'system prompt', 'developer:', 'assistant:', 'user:']
    for pattern in dangerous_patterns:
        lowered = lowered.replace(pattern, '')
    return re.sub(r'\s+', ' ', lowered).strip()


def append_audit_log(payload: dict):
    try:
        with open(AUDIT_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload, ensure_ascii=False, default=str) + '\n')
    except Exception as exc:
        logger.warning('Failed to write audit log: %s', exc)


def _single_model_call(model_name: str, messages: list[dict]) -> dict:
    if client is None:
        raise RuntimeError('GROQ_API_KEY is not configured')
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.2,
        max_tokens=1600,
        top_p=0.8,
    )
    return {'model': model_name, 'content': response.choices[0].message.content}


def call_groq_with_retry(system_prompt, messages, max_retries: int = 3, return_model: bool = False):
    """Try multiple Groq models, preferring the first one that returns successfully."""
    if client is None:
        raise RuntimeError('GROQ_API_KEY is not configured')

    groq_messages = [{'role': 'system', 'content': system_prompt}] + list(messages or [])
    last_error = None

    for model_name in MODEL_NAMES:
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=groq_messages,
                    temperature=0.2,
                    max_tokens=1600,
                    top_p=0.8,
                )
                result = response.choices[0].message.content
                print(f'  [OK] Groq [{model_name}] attempt {attempt + 1}')
                if return_model:
                    return result, model_name
                return result
            except Exception as e:
                last_error = e
                err = str(e)
                if '429' in err or 'rate' in err.lower():
                    wait = min((2**attempt) * 4, 20)
                    print(f'  [WAIT] Rate limit [{model_name}], cho {wait}s...')
                    time.sleep(wait)
                else:
                    print(f'  [ERR] [{model_name}]: {err[:160]}')
                    time.sleep(1)
    raise last_error if last_error else RuntimeError('Khong the ket noi Groq API')


class VectorSearchEngine:
    """Semantic vector search based on precomputed embeddings."""

    def __init__(self, vectors_file: str):
        self.vectors = []
        self.matrix = None
        self.meta = {}
        self._model = None
        self._load(vectors_file)

    def _load(self, path: str):
        if not os.path.exists(path):
            print(f'  [VectorSearch] Chua tim thay {path} — bo qua.')
            return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.meta = data.get('meta', {})
        self.vectors = data.get('vectors', []) or []
        if not self.vectors:
            print('  [VectorSearch] File rong, bo qua.')
            return

        dims = {len(v.get('embedding', [])) for v in self.vectors}
        if len(dims) != 1:
            raise ValueError(f'Embedding dimensions mismatch: {dims}')

        self.matrix = np.array([v['embedding'] for v in self.vectors], dtype=np.float32)
        # normalize for cosine-like dot-product search
        norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.matrix = self.matrix / norms
        print(
            f"  [VectorSearch] Tai {len(self.vectors)} vectors "
            f"({self.meta.get('dimension', 0)} chieu) model={self.meta.get('model', '?')}"
        )

    def _load_model(self) -> bool:
        if self._model is not None:
            return True
        try:
            from sentence_transformers import SentenceTransformer

            model_name = self.meta.get('model', DEFAULT_EMBEDDING_MODEL)
            print(f'  [VectorSearch] Dang tai SentenceTransformer [{model_name}] ...')
            self._model = SentenceTransformer(model_name)
            print('  [VectorSearch] Model san sang!')
            return True
        except Exception as e:
            print(f'  [VectorSearch] Khong the tai model: {e}')
            return False

    @lru_cache(maxsize=1000)
    def _cached_query_embedding(self, query: str):
        if not self._load_model():
            return tuple()
        emb = self._model.encode([query], normalize_embeddings=True)[0]
        return tuple(float(x) for x in emb)

    def encode_query(self, query: str) -> np.ndarray:
        vec = self._cached_query_embedding(query)
        if not vec:
            return np.array([], dtype=np.float32)
        return np.array(vec, dtype=np.float32)

    def search_by_vector(self, query_vec: np.ndarray, top_k: int = 6) -> list:
        if self.matrix is None or query_vec.size == 0:
            return []
        similarities = self.matrix @ query_vec
        indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for i in indices:
            payload = self.vectors[i]
            results.append(
                {
                    'product_id': payload['product_id'],
                    'name': payload['name'],
                    'similarity': float(similarities[i]),
                }
            )
        return results

    def semantic_search(self, query: str, top_k: int = 6, min_sim: float = 0.10) -> list:
        query_vec = self.encode_query(query)
        results = self.search_by_vector(query_vec, top_k)
        return [r for r in results if r['similarity'] >= min_sim]

    @property
    def is_available(self) -> bool:
        return self.matrix is not None and len(self.vectors) > 0


class ProductManager:
    def __init__(self, base_dir=None):
        self.base_dir = (
            os.path.abspath(base_dir)
            if base_dir
            else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.products = []
        self.users = []
        self.orders = []
        self.user_personas = []
        self._product_index = {}
        self._user_index = {}
        self.search_cache = {}
        self.trending_cache = []
        self.trending_model_top = []
        self.load_data()

    def _rebuild_indexes(self):
        self._product_index = {p['id']: p for p in self.products if p.get('id') is not None}
        self._user_index = {u['user_id']: u for u in self.users if u.get('user_id')}

    def load_data(self):
        data_dir = os.path.join(self.base_dir, 'data')
        csv_dir = os.path.join(data_dir, 'csv')

        with open(os.path.join(data_dir, 'products.json'), 'r', encoding='utf-8') as f:
            self.products = json.load(f) or []

        users_csv = os.path.join(csv_dir, 'users.csv')
        if os.path.exists(users_csv):
            import csv

            with open(users_csv, 'r', encoding='utf-8-sig', newline='') as f:
                self.users = list(csv.DictReader(f))
        else:
            with open(os.path.join(data_dir, 'users.json'), 'r', encoding='utf-8') as f:
                self.users = json.load(f) or []

        synthetic_orders_csv = os.path.join(csv_dir, 'synthetic_400k.csv')
        orders_csv = os.path.join(csv_dir, 'orders.csv')
        if os.path.exists(synthetic_orders_csv):
            import csv

            with open(synthetic_orders_csv, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                self.orders = [row for row in reader]
        elif os.path.exists(orders_csv):
            import csv

            with open(orders_csv, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                self.orders = [row for row in reader]
        else:
            with open(os.path.join(data_dir, 'orders.json'), 'r', encoding='utf-8') as f:
                self.orders = json.load(f) or []

        persona_path = os.path.join(data_dir, 'user_personas.json')
        if os.path.exists(persona_path):
            with open(persona_path, 'r', encoding='utf-8') as f:
                self.user_personas = json.load(f) or []
        else:
            self.user_personas = []

        self._rebuild_indexes()
        self.search_cache = {}
        for p in self.products:
            searchable = ' '.join(
                [
                    str(p.get('name', '')),
                    str(p.get('category', '')),
                    str(p.get('brand', '')),
                    str(p.get('description', '')),
                    ' '.join(p.get('tags', []) or []),
                ]
            )
            self.search_cache[p['id']] = normalize_text(sanitize_prompt_text(searchable))
        self._build_trending_cache()
        self._sync_trending_model_top()

    def _order_product_id(self, order):
        if order is None:
            return None
        pid = order.get('product_id')
        if pid is not None:
            return int(pid)
        name_product = order.get('name_product')
        if name_product:
            match = next((p for p in self.products if normalize_text(p.get('name', '')) == normalize_text(name_product)), None)
            if match:
                return int(match['id'])
        return None

    def _build_trending_cache(self):
        recent_counter = Counter(self._order_product_id(order) for order in self.orders if self._order_product_id(order) is not None)
        result = []
        total_orders = max(1, len(self.orders))
        for pid, count in recent_counter.most_common(20):
            p = self._product_index.get(pid)
            if not p:
                continue
            payload = dict(p)
            payload['trend_score'] = round(count / total_orders, 4)
            payload['trend_count'] = count
            result.append(payload)
        self.trending_cache = result

    def _sync_trending_model_top(self):
        """Sync ProductManager trending with recommender M5 when available."""
        try:
            models_dir = os.path.join(self.base_dir, 'models', 'm5_popularity.json')
            if not os.path.exists(models_dir):
                self.trending_model_top = []
                return
            with open(models_dir, 'r', encoding='utf-8') as f:
                raw = json.load(f) or {}
            trending_rows = raw.get('trending_top', []) or []
            synced = []
            for row in trending_rows:
                pid = row.get('product_id')
                product = self._product_index.get(int(pid))
                if not product:
                    continue
                payload = dict(product)
                payload['trend_ratio'] = float(row.get('trend_ratio', 0) or 0)
                payload['trend_count'] = int(row.get('raw_count', 0) or 0)
                payload['popularity_score'] = float(row.get('popularity_score', 0) or 0)
                synced.append(payload)
            self.trending_model_top = synced
        except Exception:
            self.trending_model_top = []

    def get_all_products(self):
        return self.products

    def get_product_by_id(self, product_id):
        return self._product_index.get(product_id)

    def search_products(self, query):
        q = normalize_text(query)
        if not q:
            return []
        results = []
        for p in self.products:
            searchable = self.search_cache.get(p['id'], '')
            if q in searchable:
                results.append(p)
        if results:
            return results
        tokens = [t for t in q.split() if len(t) > 2]
        if not tokens:
            return []
        scored = []
        for p in self.products:
            searchable = self.search_cache.get(p['id'], '')
            score = sum(1 for t in tokens if t in searchable)
            if score:
                scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored]

    def filter_products(self, category=None, brand=None, min_price=None, max_price=None, tags=None, sort_by=None):
        results = list(self.products)
        if category:
            c = normalize_text(category)
            results = [p for p in results if normalize_text(p.get('category', '')) == c]
        if brand:
            b = normalize_text(brand)
            results = [p for p in results if normalize_text(p.get('brand', '')) == b]
        if min_price is not None:
            results = [p for p in results if float(p.get('price', 0) or 0) >= min_price]
        if max_price is not None:
            results = [p for p in results if float(p.get('price', 0) or 0) <= max_price]
        if tags:
            tag_list = {normalize_text(t) for t in tags}
            results = [p for p in results if any(normalize_text(t) in tag_list for t in p.get('tags', []))]

        if sort_by == 'price_asc':
            results.sort(key=lambda x: float(x.get('price', 0) or 0))
        elif sort_by == 'price_desc':
            results.sort(key=lambda x: float(x.get('price', 0) or 0), reverse=True)
        elif sort_by == 'rating':
            results.sort(key=lambda x: float(x.get('rating', 0) or 0), reverse=True)
        elif sort_by == 'discount':
            results.sort(key=lambda x: float(x.get('discount', 0) or 0), reverse=True)
        elif sort_by == 'reviews':
            results.sort(key=lambda x: int(x.get('reviews', 0) or 0), reverse=True)
        return results

    def get_user_profile(self, user_id):
        return self._user_index.get(user_id)

    def get_user_orders(self, user_id):
        return [o for o in self.orders if o.get('user_id') == user_id]

    def get_product_reviews(self, product_id):
        return [o for o in self.orders if o.get('product_id') == product_id and o.get('review')]

    def get_top_products(self, n=5, category=None):
        products = list(self.products)
        if category:
            c = normalize_text(category)
            products = [p for p in products if normalize_text(p.get('category', '')) == c]
        products.sort(key=lambda x: (float(x.get('rating', 0) or 0), int(x.get('reviews', 0) or 0)), reverse=True)
        return products[:n]

    def get_trending_products(self, n=5):
        if self.trending_model_top:
            return [dict(p) for p in self.trending_model_top[:n]]
        if self.trending_cache:
            trending = []
            for p in self.trending_cache[:n]:
                payload = dict(p)
                payload['trend_ratio'] = payload.get('trend_score', 0)
                trending.append(payload)
            return trending
        product_order_count = Counter(self._order_product_id(order) for order in self.orders if self._order_product_id(order) is not None)
        trending = []
        total_orders = max(1, len(self.orders))
        for pid, count in product_order_count.most_common(n):
            product = self.get_product_by_id(pid)
            if product:
                payload = dict(product)
                payload['trend_ratio'] = count / total_orders
                payload['trend_count'] = count
                trending.append(payload)
        return trending

    def format_price(self, price):
        return f"{float(price):,.0f}đ".replace(',', '.')

    def product_to_text(self, product):
        specs = product.get('specs', {}) or {}
        specs_text = ', '.join([f'{k}: {v}' for k, v in specs.items()]) if specs else 'Chua co thong so'
        return (
            f"[ID:{product['id']}] {product['name']}\n"
            f"  - Danh muc: {product['category']} | Thuong hieu: {product['brand']}\n"
            f"  - Gia: {self.format_price(product['price'])} (goc: {self.format_price(product['original_price'])}, giam {product['discount']}%)\n"
            f"  - Danh gia: {product['rating']}/5 ({product['reviews']} danh gia)\n"
            f"  - Mo ta: {product.get('description', '')}\n"
            f"  - Thong so: {specs_text}\n"
            f"  - Tags: {', '.join(product.get('tags', []) or [])}\n"
            f"  - Con hang: {product.get('stock', 0)} san pham\n"
        )

    def compact_product_text(self, product):
        return (
            f"[{product['id']}]\n"
            f"Ten: {product['name']}\n"
            f"Thuong hieu: {product['brand']}\n"
            f"Danh muc: {product['category']}\n"
            f"Gia: {self.format_price(product['price'])}\n"
            f"Danh gia: {product['rating']}/5\n"
            f"Tags: {', '.join(product.get('tags', [])[:3])}\n"
        )

    def get_content_based_recommendations(self, product_id, n=4):
        target = self.get_product_by_id(product_id)
        if not target:
            return []
        scores = []
        target_tags = set(target.get('tags', []) or [])
        for p in self.products:
            if p['id'] == product_id:
                continue
            score = 0
            if p.get('category') == target.get('category'):
                score += 3
            if p.get('brand') == target.get('brand'):
                score += 2
            common_tags = set(p.get('tags', []) or []) & target_tags
            score += len(common_tags)
            price_ratio = min(float(p.get('price', 0) or 0), float(target.get('price', 0) or 0)) / max(
                float(p.get('price', 0) or 0), float(target.get('price', 0) or 0), 1.0
            )
            if price_ratio > 0.7:
                score += 2
            scores.append((score, p))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scores[:n]]

    def get_collaborative_recommendations(self, user_id, n=4):
        target_user = self.get_user_profile(user_id)
        if not target_user:
            return self.get_top_products(n)

        target_purchased = set(target_user.get('purchase_history', []))
        target_browsed = set(target_user.get('browsing_history', []))

        user_scores = []
        for u in self.users:
            if u['user_id'] == user_id:
                continue
            other_purchased = set(u.get('purchase_history', []))
            other_browsed = set(u.get('browsing_history', []))
            common = (target_purchased | target_browsed) & (other_purchased | other_browsed)
            total = (target_purchased | target_browsed) | (other_purchased | other_browsed)
            similarity = len(common) / len(total) if total else 0
            user_scores.append((similarity, u))

        user_scores.sort(key=lambda x: x[0], reverse=True)
        candidate_products = Counter()
        for sim, u in user_scores[:3]:
            for pid in u.get('purchase_history', []):
                if pid not in target_purchased:
                    candidate_products[pid] += sim
            for pid in u.get('wishlist', []):
                if pid not in target_purchased:
                    candidate_products[pid] += sim * 0.5

        result = []
        for pid, _ in candidate_products.most_common(n):
            p = self.get_product_by_id(pid)
            if p:
                result.append(p)
        if len(result) < n:
            for p in self.get_top_products(n):
                if p not in result:
                    result.append(p)
        return result[:n]

    def get_hybrid_recommendations(self, user_id=None, product_id=None, n=4):
        cbf_results = self.get_content_based_recommendations(product_id, n) if product_id else []
        cf_results = self.get_collaborative_recommendations(user_id, n) if user_id else []
        seen = set()
        merged = []
        for p in cbf_results + cf_results:
            if p['id'] not in seen:
                seen.add(p['id'])
                merged.append(p)
        if len(merged) < n:
            for p in self.get_top_products(n):
                if p['id'] not in seen:
                    seen.add(p['id'])
                    merged.append(p)
        return merged[:n]

    def get_analytics(self):
        products = self.products
        orders = self.orders

        revenue_by_category = defaultdict(float)
        orders_by_category = defaultdict(int)
        for o in orders:
            p = self.get_product_by_id(o.get('product_id'))
            if p:
                revenue_by_category[p['category']] += float(o.get('total_price', 0) or 0)
                orders_by_category[p['category']] += 1

        product_order_count = Counter(o.get('product_id') for o in orders if o.get('product_id') is not None)
        top_selling = []
        for pid, count in product_order_count.most_common(5):
            p = self.get_product_by_id(pid)
            if p:
                top_selling.append({**p, 'order_count': count})

        price_ranges = {'<5tr': 0, '5-10tr': 0, '10-20tr': 0, '20-35tr': 0, '>35tr': 0}
        for p in products:
            price = float(p.get('price', 0) or 0)
            if price < 5_000_000:
                price_ranges['<5tr'] += 1
            elif price < 10_000_000:
                price_ranges['5-10tr'] += 1
            elif price < 20_000_000:
                price_ranges['10-20tr'] += 1
            elif price < 35_000_000:
                price_ranges['20-35tr'] += 1
            else:
                price_ranges['>35tr'] += 1

        rating_dist = Counter()
        for p in products:
            rating_dist[str(int(float(p.get('rating', 0) or 0)))] += 1

        brand_stats = defaultdict(lambda: {'count': 0, 'total_revenue': 0, 'avg_rating': 0, 'ratings': []})
        for p in products:
            brand_stats[p['brand']]['count'] += 1
            brand_stats[p['brand']]['ratings'].append(float(p.get('rating', 0) or 0))
        for brand in brand_stats:
            ratings = brand_stats[brand]['ratings']
            brand_stats[brand]['avg_rating'] = round(sum(ratings) / len(ratings), 2) if ratings else 0
            del brand_stats[brand]['ratings']
        for o in orders:
            p = self.get_product_by_id(o.get('product_id'))
            if p:
                brand_stats[p['brand']]['total_revenue'] += float(o.get('total_price', 0) or 0)

        monthly_orders = defaultdict(int)
        monthly_revenue = defaultdict(float)
        for o in orders:
            date = str(o.get('date', ''))
            month = date[:7] if len(date) >= 7 else 'unknown'
            monthly_orders[month] += 1
            monthly_revenue[month] += float(o.get('total_price', 0) or 0)

        avg_order_rating = round(sum(float(o.get('rating', 0) or 0) for o in orders) / len(orders), 2) if orders else 0
        avg_product_rating = round(sum(float(p.get('rating', 0) or 0) for p in products) / len(products), 2) if products else 0
        avg_discount = round(sum(float(p.get('discount', 0) or 0) for p in products) / len(products), 1) if products else 0

        return {
            'summary': {
                'total_products': len(products),
                'total_users': len(self.users),
                'total_orders': len(orders),
                'total_revenue': sum(float(o.get('total_price', 0) or 0) for o in orders),
                'avg_rating': avg_product_rating,
                'avg_order_rating': avg_order_rating,
                'avg_discount': avg_discount,
            },
            'revenue_by_category': dict(revenue_by_category),
            'orders_by_category': dict(orders_by_category),
            'top_selling': top_selling,
            'price_distribution': price_ranges,
            'rating_distribution': dict(rating_dist),
            'brand_stats': {k: dict(v) for k, v in brand_stats.items()},
            'monthly_orders': dict(sorted(monthly_orders.items())),
            'monthly_revenue': dict(sorted(monthly_revenue.items())),
            'categories': sorted({p['category'] for p in products}),
            'brands': sorted({p['brand'] for p in products}),
        }


class EcommerceAdvisor:
    def __init__(self, product_manager, vector_engine=None, ai_recommender=None):
        self.pm = product_manager
        self.vector_engine = vector_engine
        self.ai_recommender = ai_recommender
        self.conversation_histories = {}
        self.session_context = {}
        self.max_retrieved_products = 24
        self.max_context_products = 10
        self._last_retrieval_reasons = {}
        self._last_audit = None

    def _get_recommender_models_used(self):
        if not self.ai_recommender:
            return ['pm_hybrid']
        try:
            info = self.ai_recommender.model_info()
            keys = sorted(info.keys())
            return keys if keys else ['ai_recommender']
        except Exception:
            return ['ai_recommender']

    def _log_ai_audit(self, payload: dict):
        append_audit_log(payload)
        self._last_audit = payload

    def _build_system_prompt(self, user_profile=None, extra_context='', is_first_turn=False):
        prompt = """Ban la nhan vien tu van ban hang cua TechStore: than thien, niem no, chuyen nghiep, va rat dang tin cay.

## MUC TIEU CHINH
- Tu van dung san pham theo nhu cau thuc te cua khach hang.
- Chi dua ra thong tin co trong du lieu duoc cung cap.
- Khong bia san pham, gia, thong so, ton kho, khuyen mai hay danh gia.
- Luon giao tiep tu nhien nhu mot nhan vien ban hang that su, khong may moc.

## NGUYEN TAC BAT BUOC
1. Chi dung thong tin co trong du lieu dau vao, context, API, DB, hoac lich su hoi thoai dang tin cay.
2. Neu khong du du lieu de ket luan, noi ro la chua du thong tin va hoi toi da 1-2 cau ngan gon.
3. Khong tu suy doan ten san pham, gia, thuong hieu, thong so, ton kho, hay uu dai.
4. Neu nguoi dung hoi ve san pham cu the ma khong co trong du lieu, hay noi khong tim thay va de xuat phuong an tuong duong trong du lieu.
5. Neu co nhieu lua chon phu hop, chi de xuat toi da 3 san pham tot nhat.
6. Neu nguoi dung hoi theo thuong hieu, chi de xuat san pham dung thuong hieu do.
7. Neu nguoi dung hoi dang "top", "trending", "ban chay", "quan tam nhat", chi dung du lieu xep hang that tu nguon duoc cung cap, khong tu tao danh sach.
8. Khi nhac den gia, phai neu dung gia hien tai, gia goc, va % giam neu co.
9. Khi nhac den san pham, nen kem ten, danh muc, thuong hieu, gia, danh gia, so luong con hang neu du lieu co.
10. Khong duoc noi rang ban "tu biet" hay "tu suy ra" neu du lieu khong co.

## PHONG CACH TRA LOI
- Niem no, de gan, noan ngoan nhung khong khoa truong.
- Noi chuyen nhu mot nhan vien tu van that su, khong gia lap qua muc.
- Uu tien ro rang, de hieu, co bullet points khi can.
- Khong qua dai dong, khong bao cao hoa.
- Neu thieu du lieu, noi mem mai va goi y buoc tiep theo.
- Moi cau tra loi nen ket thuc bang 1 cau hoi mo nhe nhang de dan dắt tiep.

## CAC TINH HUONG THUONG GAP
- Neu khach hoi chung chung: hoi lai ngan gon ve ngan sach, nhu cau, hoac thuong hieu.
- Neu khach da noi ro nhu cau: di thang vao goi y phu hop nhat.
- Neu khach so sanh san pham: neu diem manh/yeu theo du lieu, khach quan.
- Neu khach muon mua nhanh: uu tien san pham phu hop nhat, ngan gon va ro rang.
- Neu khong co du lieu phu hop: noi "Hien minh chua thay san pham phu hop trong du lieu, ban cho minh them mot chut thong tin nhe."

## DINH DANG TRA LOI
- Bat dau bang loi chao lich su neu la tin nhan dau tien cua session.
- Gioi thieu ngan ve TechStore/web o tin dau tien neu can.
- Chi de xuat toi da 3 san pham phu hop nhat, sap xep uu tien ro rang.
- Moi san pham nen co:
  - Gia hien tai + gia goc + % giam
  - Danh gia trung binh + so luong danh gia
  - Do pho bien (dua tren reviews/so don/duoc goi y)
  - Uu diem noi bat (2-3 y gon)
  - Ly do phu hop voi nhu cau nguoi dung
- Neu user chi ro tam gia/nhu cau, khong hoi lai neu khong that su can thiet; thay vao do dua ra de xuat co so va cau hoi xac nhan cuoi.

## QUY TAC CHOT CUA
- Moi tra loi nen ket thuc bang 1 cau hoi nhe de mo rong cuoc tu van.
- Vi du: "Ban muon minh loc tiep theo ngan sach hay thuong hieu khong?"
- Khong hoi lai neu thong tin da du ro.

## MAU GIONG VAN
- "Dạ, mình gợi ý bạn vài lựa chọn phù hợp nhất nhé."
- "Mình chưa thấy đủ dữ liệu để khẳng định, bạn cho mình thêm một chút thông tin được không?"
- "Nếu bạn thích, mình có thể lọc tiếp theo ngân sách hoặc thương hiệu."
- "Dựa trên dữ liệu hiện có, mẫu này đang là lựa chọn phù hợp nhất."

## QUAN TRONG
- Luon uu tien do chinh xac hon su tu tin.
- Khong bia de lam cau tra loi hay hon.
- Neu du lieu thieu, hay noi thieu mot cach lich su va ho tro nguoi dung tiep tuc.
"""
        if is_first_turn:
            prompt += """

## YEU CAU DAC BIET CHO TIN NHAN DAU TIEN:
- Bat buoc mo dau bang loi chao + gioi thieu ngan ve TechStore/web va chuyen mon.
- Sau phan gioi thieu, hoi khach 1-2 cau de lay nhanh nhu cau va tam gia.
"""
        if user_profile:
            prompt += f"""
## THONG TIN KHACH HANG (CA NHAN HOA):
- Ten: {user_profile['name']} | Tuoi: {user_profile['age']} | Gioi tinh: {user_profile['gender']}
- Nghe nghiep: {user_profile['occupation']}
- Ngan sach phu hop: {user_profile['budget_range']}
- So thich/Nhu cau: {', '.join(user_profile['preferences'])}
=> Hay CA NHAN HOA loi tu van theo thong tin nay.
"""
        if extra_context:
            prompt += f'\n{extra_context}'
        return prompt

    def _normalize_text(self, text: str) -> str:
        return normalize_text(text)

    def _extract_query_constraints(self, user_message: str):
        normalized = self._normalize_text(user_message)
        category_keywords = {
            'Dien thoai': ['dien thoai', 'phone', 'iphone', 'smartphone', 'mobile', 'dt'],
            'Laptop': ['laptop', 'may tinh xach tay', 'macbook', 'notebook', 'pc', 'may tinh'],
            'Phu kien': ['tai nghe', 'airpods', 'phu kien', 'sac du phong', 'sac', 'chuot', 'ban phim', 'loa', 'headphone'],
            'Dong ho thong minh': ['dong ho', 'smartwatch', 'watch', 'apple watch', 'galaxy watch'],
            'May tinh bang': ['tablet', 'may tinh bang', 'ipad', 'tab'],
            'May anh': ['may anh', 'mirrorless', 'sony a7', 'fuji', 'canon'],
        }
        detected_categories = [cat for cat, keywords in category_keywords.items() if any(kw in normalized for kw in keywords)]

        detected_brand = None
        catalog_brands = sorted({(p.get('brand') or '').strip() for p in self.pm.products if p.get('brand')})
        for brand in catalog_brands:
            if self._normalize_text(brand) in normalized:
                detected_brand = brand
                break

        if not detected_brand:
            known_brands = ['nokia', 'apple', 'iphone', 'samsung', 'xiaomi', 'oppo', 'realme', 'sony', 'dell', 'asus', 'hp', 'acer', 'lenovo']
            for brand in known_brands:
                if brand in normalized:
                    detected_brand = 'Apple' if brand == 'iphone' else brand.title()
                    break

        return {'normalized_message': normalized, 'categories': detected_categories, 'brand': detected_brand}

    def _score_product(self, product, constraints, user_message):
        score = 0.0
        reasons = []
        normalized_msg = constraints['normalized_message']
        detected_categories = constraints['categories']
        detected_brand = constraints['brand']

        product_brand = self._normalize_text(product.get('brand', ''))
        product_category = self._normalize_text(product.get('category', ''))
        product_name = self._normalize_text(product.get('name', ''))
        product_tags = [self._normalize_text(t) for t in product.get('tags', [])]

        if detected_brand and product_brand == self._normalize_text(detected_brand):
            score += 5.0
            reasons.append('khop thuong hieu')
        elif detected_brand:
            return -999.0, []

        if detected_categories:
            allowed_categories = {self._normalize_text(c) for c in detected_categories}
            if product_category in allowed_categories:
                score += 4.0
                reasons.append('khop danh muc')
            else:
                score -= 1.5

        if any(t and t in normalized_msg for t in product_tags):
            score += 2.0
            reasons.append('khop tu khoa nhu cau')

        need_keywords = {
            'gaming': ['gaming', 'choi game', 'game', 'rtx', 'fps'],
            'sinh vien': ['sinh vien', 'hoc sinh', 'di hoc', 'student'],
            'van phong': ['van phong', 'lam viec', 'office', 'cong viec', 'doanh nhan'],
            'chup anh': ['chup anh', 'nhiep anh', 'chup hinh', 'camera'],
            'pin trau': ['pin trau', 'pin lau', 'pin khoe', 'dung lau', 'battery'],
            'cao cap': ['cao cap', 'flagship', 'premium', 'xin', 'tot nhat', 'dinh'],
            'gia re': ['gia re', 're', 'tiet kiem', 'binh dan', 'gia tot', 're nhat'],
            'mong nhe': ['mong', 'nhe', 'ultrabook', 'gon', 'compact'],
            'sang tao': ['sang tao', 'thiet ke', 've', 'design', 'do hoa', 'edit video'],
            'lap trinh': ['lap trinh', 'code', 'dev', 'developer', 'programmer'],
        }
        for tag, kws in need_keywords.items():
            if any(kw in normalized_msg for kw in kws) and tag in product_tags:
                score += 2.5
                reasons.append(f'phu hop nhu cau {tag}')

        price_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:trieu|tr\b)', normalized_msg)
        min_price, max_price = None, None
        if price_match:
            prices = [float(p) * 1_000_000 for p in price_match]
            under_keywords = ['duoi', 'khong qua', 'toi da', 'max', '<']
            from_keywords = ['tu', 'tren', 'it nhat', 'min', '>']
            if any(kw in normalized_msg for kw in under_keywords):
                max_price = max(prices)
            elif any(kw in normalized_msg for kw in from_keywords) and len(prices) == 1:
                min_price = prices[0]
            elif len(prices) >= 2:
                min_price, max_price = min(prices), max(prices)
            else:
                max_price = prices[0]

        price = float(product.get('price', 0) or 0)
        if min_price is not None and price >= min_price:
            score += 1.5
            reasons.append('nam trong nguong gia toi thieu')
        if max_price is not None and price <= max_price:
            score += 1.5
            reasons.append('nam trong nguong gia toi da')
        if min_price is not None and max_price is not None and min_price <= price <= max_price:
            score += 2.0
            reasons.append('nam trong khoang gia')

        rating = float(product.get('rating', 0) or 0)
        reviews = int(product.get('reviews', 0) or 0)
        discount = float(product.get('discount', 0) or 0)
        stock = int(product.get('stock', 0) or 0)

        if rating >= 4.5:
            reasons.append('danh gia cao')
        if reviews >= 1000:
            reasons.append('nhieu danh gia')
        if discount >= 15:
            reasons.append('giam gia tot')
        if stock > 0:
            reasons.append('con hang')

        score += rating * 0.8
        score += min(reviews / 1000.0, 3.0)
        score += min(discount / 10.0, 2.5)
        if stock > 0:
            score += 0.5

        if product_name and product_name in normalized_msg:
            score += 2.5
            reasons.append('khop ten san pham')

        return score, reasons

    def _retrieve_relevant_products(self, user_message):
        constraints = self._extract_query_constraints(user_message)
        normalized_msg = constraints['normalized_message']
        detected_categories = constraints['categories']
        detected_brand = constraints['brand']

        ranked = []
        for product in self.pm.get_all_products():
            score, reasons = self._score_product(product, constraints, user_message)
            if score > -500:
                ranked.append((score, product, reasons))

        ranked.sort(key=lambda x: x[0], reverse=True)
        unique = []
        seen = set()
        reason_map = {}
        for score, p, reasons in ranked:
            if p['id'] not in seen:
                seen.add(p['id'])
                unique.append(p)
                reason_map[p['id']] = reasons

        strict_mode = bool(detected_brand or detected_categories)
        broad_query = not strict_mode and not normalized_msg.strip()

        if len(unique) < 5 and self.vector_engine and self.vector_engine.is_available and not strict_mode:
            try:
                vec_results = self.vector_engine.semantic_search(user_message, top_k=6, min_sim=0.18)
                for vr in vec_results:
                    p = self.pm.get_product_by_id(vr['product_id'])
                    if p and p['id'] not in seen:
                        seen.add(p['id'])
                        unique.append(p)
                        reason_map[p['id']] = ['semantic khop y dinh']
            except Exception as e:
                print(f'  [VectorSearch] Loi fallback: {e}')

        if self.ai_recommender and unique and not strict_mode and not broad_query:
            try:
                pivot_id = unique[0]['id']
                tfidf_ids = {x['product_id'] for x in self.ai_recommender.tfidf_similar(pivot_id, 8)}
                itemcf_ids = {x['product_id'] for x in self.ai_recommender.item_cf_similar(pivot_id, 8)}
                boosted_ids = (tfidf_ids | itemcf_ids) - seen
                for pid in list(boosted_ids)[:4]:
                    p = self.pm.get_product_by_id(pid)
                    if p and p['id'] not in seen:
                        seen.add(pid)
                        unique.append(p)
                        reason_map[p['id']] = ['duoc tang cuong boi recommender']
            except Exception as e:
                print(f'  [ML boost] {e}')

        if detected_brand:
            unique = [p for p in unique if self._normalize_text(p.get('brand', '')) == self._normalize_text(detected_brand)]
        elif detected_categories:
            allowed = {self._normalize_text(c) for c in detected_categories}
            unique = [p for p in unique if self._normalize_text(p.get('category', '')) in allowed]

        self._last_retrieval_reasons = {p['id']: reason_map.get(p['id'], []) for p in unique}
        return unique[: self.max_retrieved_products]

    def _find_persona(self, user_id=None, user_profile=None):
        personas = getattr(self.pm, 'user_personas', []) or []
        if not personas:
            return None

        if user_id:
            normalized_user_id = self._normalize_text(user_id)
            for persona in personas:
                pid = self._normalize_text(persona.get('persona_id', ''))
                if pid and pid == normalized_user_id:
                    return persona

        if user_profile:
            occupation = self._normalize_text(user_profile.get('occupation', ''))
            age = user_profile.get('age')
            for persona in personas:
                if occupation and occupation in self._normalize_text(persona.get('interests', '')):
                    return persona
                if age and abs(int(persona.get('age', 0) or 0) - int(age)) <= 3:
                    return persona

        return personas[0]

    def _get_user_context(self, user_id, user_profile=None):
        user = user_profile or self.pm.get_user_profile(user_id)
        if not user and not user_id:
            return ''

        ctx = ''
        if user:
            ctx += '\n## LICH SU MUA HANG:\n'
            for o in self.pm.get_user_orders(user_id):
                p = self.pm.get_product_by_id(o['product_id'])
                if p:
                    ctx += f"- Da mua: {p['name']} ({o['date']}) - {o.get('rating', 0)}/5 sao\n"
            if user.get('wishlist'):
                ctx += '\n## WISHLIST:\n'
                for pid in user['wishlist']:
                    p = self.pm.get_product_by_id(pid)
                    if p:
                        ctx += f"- {p['name']} - {self.pm.format_price(p['price'])}\n"

        persona = self._find_persona(user_id=user_id, user_profile=user)
        if persona:
            ctx += '\n## PERSONA BO SUNG:\n'
            ctx += f"- Do tuoi: {persona.get('age', '')}\n"
            ctx += f"- Gioi tinh: {persona.get('gender', '')}\n"
            ctx += f"- Thu nhap: {persona.get('income', '')}\n"
            ctx += f"- So thich: {persona.get('interests', '')}\n"
            ctx += f"- Muc tieu chi tieu: {persona.get('average_order_value', '')}\n"
            ctx += f"- Danh muc uu tien: {persona.get('product_category_preference', '')}\n"
            ctx += f"- Muc do mua sam: {persona.get('purchase_frequency', '')}\n"
            ctx += f"- Tong chi tieu: {persona.get('total_spending', '')}\n"
        return ctx

    def chat(self, user_message, session_id='default', user_id=None):
        if session_id not in self.conversation_histories:
            self.conversation_histories[session_id] = []
        history = self.conversation_histories[session_id]
        is_first_turn = len(history) == 0
        audit_context = {
            'session_id': session_id,
            'user_id': user_id,
            'user_message': user_message,
            'matched': False,
        }

        constraints = self._extract_query_constraints(user_message)
        requested_brand = constraints['brand']
        requested_categories = constraints['categories']

        normalized_message = self._normalize_text(user_message)
        if any(k in normalized_message for k in ['trending', 'ban chay', 'top san pham', 'thinh hanh', 'quan tam nhat']):
            m = re.search(r'\btop\s*(\d+)\b', normalized_message)
            top_n = int(m.group(1)) if m else 10
            top_n = max(1, min(top_n, 10))
            top_items = self.pm.get_trending_products(n=top_n)
            lines = [
                f'Dưới đây là top {top_n} sản phẩm Trending tại TechStore (lấy từ data thật):',
                '',
            ]
            for idx, p in enumerate(top_items, 1):
                lines.append(
                    f"{idx}. **{p['name']}** - {p['category']} / {p['brand']}\n"
                    f"   - product_id: {p['id']}\n"
                    f"   - Giá: {self.pm.format_price(p['price'])} (gốc {self.pm.format_price(p['original_price'])}, giảm {p['discount']}%)\n"
                    f"   - Đánh giá: {p['rating']}/5 ({p['reviews']} đánh giá)\n"
                    f"   - Còn hàng: {p['stock']}\n"
                    f"   - trend_ratio: {p.get('trend_ratio', 0):.4f}"
                )
            response = '\n'.join(lines)
            history.clear()
            history.append({'role': 'user', 'content': user_message})
            history.append({'role': 'assistant', 'content': response})
            self.conversation_histories[session_id] = history
            audit_payload = {
                'timestamp': time.time(),
                'session_id': session_id,
                'user_id': user_id,
                'query': user_message,
                'answer_source': 'api.products.trending',
                'model_used': 'rule_based_trending',
                'recommender_models_used': [],
                'retrieved_count': 0,
                'returned_count': len(top_items),
                'requested_brand': None,
                'requested_categories': [],
                'retrieved_products': [],
                'returned_products': [{
                    'id': p['id'],
                    'name': p['name'],
                    'category': p['category'],
                    'brand': p['brand'],
                    'price': p['price'],
                    'trend_ratio': p.get('trend_ratio', 0),
                } for p in top_items],
            }
            self._log_ai_audit(audit_payload)
            logger.info(
                "[AI TRACE] session=%s | user=%s | llm=rule_based_trending | recommender=none | retrieved=0 | returned=%s",
                session_id,
                user_id or '-',
                len(top_items),
            )
            return {
                'response': response,
                'relevant_products': [_fmt_product(p, self.pm) for p in top_items],
                'session_id': session_id,
                'model_used': 'rule_based_trending',
                'recommender_models_used': [],
                'answer_source': 'api.products.trending',
                'source': 'api.products.trending',
                'trace': {
                    'sources': ['top_products'],
                    'retrieved_count': 0,
                    'retrieved_products': [],
                    'returned_count': len(top_items),
                    'requested_brand': None,
                    'requested_categories': [],
                    'has_user_context': False,
                    'has_rec_context': False,
                    'is_first_turn': is_first_turn,
                },
            }

        relevant_products = self._retrieve_relevant_products(user_message)

        if requested_brand and not relevant_products:
            response = (
                f"Xin chao! Hien tai TechStore chua co san pham thuong hieu {requested_brand} theo nhu cau ban vua hoi. "
                'Ban co muon minh de xuat cac lua chon tuong duong theo tam gia/nhu cau khong?'
            )
            history.append({'role': 'user', 'content': user_message})
            history.append({'role': 'assistant', 'content': response})
            self.conversation_histories[session_id] = history
            audit_payload = {
                'timestamp': time.time(),
                'session_id': session_id,
                'user_id': user_id,
                'query': user_message,
                'answer_source': 'api.chat.no_brand_match',
                'model_used': 'rule_based_no_brand_match',
                'recommender_models_used': [],
                'retrieved_count': 0,
                'returned_count': 0,
                'requested_brand': requested_brand,
                'requested_categories': requested_categories,
                'retrieved_products': [],
                'returned_products': [],
            }
            self._log_ai_audit(audit_payload)
            logger.info(
                "[AI TRACE] session=%s | user=%s | llm=rule_based_no_brand_match | recommender=none | retrieved=0 | returned=0",
                session_id,
                user_id or '-',
            )
            return {
                'response': response,
                'relevant_products': [],
                'session_id': session_id,
                'model_used': 'rule_based_no_brand_match',
                'recommender_models_used': [],
                'answer_source': 'api.chat.no_brand_match',
                'source': 'api.chat.no_brand_match',
                'trace': {
                    'sources': ['product_retrieval'],
                    'retrieved_count': 0,
                    'retrieved_products': [],
                    'returned_count': 0,
                    'requested_brand': requested_brand,
                    'requested_categories': requested_categories,
                    'has_user_context': False,
                    'has_rec_context': False,
                    'is_first_turn': is_first_turn,
                },
            }

        products_context = '\n## DU LIEU SAN PHAM CO SAN:\n'
        for p in relevant_products[: self.max_context_products]:
            reasons = self._last_retrieval_reasons.get(p['id'], [])
            reason_text = f"\n  - Ly do chon: {', '.join(reasons)}" if reasons else ''
            products_context += self.pm.product_to_text(p) + reason_text + '\n'

        rec_context = ''
        if user_id and self.ai_recommender:
            try:
                hybrid_ids = self.ai_recommender.hybrid_recommend(user_id=user_id, top_k=3)
                hybrid_products = [self.pm.get_product_by_id(x['product_id']) for x in hybrid_ids]
                hybrid_products = [p for p in hybrid_products if p]
                if hybrid_products:
                    rec_context = '\n## GOI Y DANH RIENG (AI MULTI-MODEL):\n'
                    for p in hybrid_products:
                        rec_context += f"- {p['name']} - {self.pm.format_price(p['price'])}\n"
            except Exception:
                pass
        elif user_id:
            recs = self.pm.get_hybrid_recommendations(user_id=user_id, n=3)
            if recs:
                rec_context = '\n## GOI Y DANH RIENG CHO KHACH HANG NAY:\n'
                for p in recs:
                    rec_context += f"- {p['name']} - {self.pm.format_price(p['price'])}\n"

        user_profile = self.pm.get_user_profile(user_id) if user_id else None
        user_context = self._get_user_context(user_id, user_profile=user_profile) if (user_id or user_profile) else ''
        system_prompt = self._build_system_prompt(
            user_profile,
            products_context + rec_context + user_context,
            is_first_turn=is_first_turn,
        )
        if requested_brand:
            system_prompt += (
                f"\n## RANG BUOC THUONG HIEU:\n"
                f"- Khach dang hoi ro thuong hieu {requested_brand}. "
                'Chi duoc de xuat san pham dung thuong hieu nay, khong chen thuong hieu khac neu chua duoc khach cho phep.'
            )

        messages = [{'role': m['role'], 'content': m['content']} for m in history[-12:]]
        messages.append({'role': 'user', 'content': user_message})

        llm_model_used = 'unknown'
        trace_sources = []
        retrieved_products_trace = []
        for p in relevant_products[: self.max_context_products]:
            reasons = self._last_retrieval_reasons.get(p['id'], [])
            retrieved_products_trace.append(
                {
                    'id': p['id'],
                    'name': p['name'],
                    'category': p['category'],
                    'brand': p['brand'],
                    'price': p['price'],
                    'reasons': reasons,
                }
            )
        if retrieved_products_trace:
            trace_sources.append('product_retrieval')
        if user_id and (self.ai_recommender or self.pm.get_hybrid_recommendations(user_id=user_id, n=1)):
            trace_sources.append('personalized_recommendation')
        if user_context:
            trace_sources.append('user_context')
        if rec_context:
            trace_sources.append('recommendation_context')
        retrieved_products_count = len(relevant_products)

        try:
            ai_response, llm_model_used = call_groq_with_retry(
                system_prompt,
                messages,
                return_model=True,
            )
            ai_response = ai_response.strip()
            if len(relevant_products) >= 3:
                ai_response += '\n\nBạn muốn mình lọc tiếp theo giá, thương hiệu hay nhu cầu sử dụng không?'
        except Exception as e:
            error_str = str(e)
            llm_model_used = 'fallback_error'
            if '429' in error_str or 'rate' in error_str.lower():
                ai_response = 'Hệ thống đang quá tải, vui lòng thử lại sau vài giây!'
            else:
                ai_response = f'Xin loi, co loi xay ra: {error_str[:150]}'

        history.append({'role': 'user', 'content': user_message})
        history.append({'role': 'assistant', 'content': ai_response})
        self.conversation_histories[session_id] = history

        pivot_pid = relevant_products[0]['id'] if relevant_products else None
        if self.ai_recommender:
            try:
                hybrid_ids = self.ai_recommender.hybrid_recommend(user_id=user_id, product_id=pivot_pid, top_k=6)
                rec_products = [self.pm.get_product_by_id(x['product_id']) for x in hybrid_ids]
                rec_products = [p for p in rec_products if p]
            except Exception:
                rec_products = self.pm.get_hybrid_recommendations(user_id=user_id, product_id=pivot_pid, n=6)
        else:
            rec_products = self.pm.get_hybrid_recommendations(user_id=user_id, product_id=pivot_pid, n=6)

        if requested_brand:
            rec_products = [p for p in rec_products if self._normalize_text(p.get('brand', '')) == self._normalize_text(requested_brand)]
        if requested_categories:
            allowed_categories = {self._normalize_text(c) for c in requested_categories}
            rec_products = [p for p in rec_products if self._normalize_text(p.get('category', '')) in allowed_categories]

        recommender_models_used = self._get_recommender_models_used()
        answer_source = 'llm.groq' if llm_model_used != 'fallback_error' else 'fallback_error'
        returned_products_formatted = [_fmt_product(p, self.pm) for p in rec_products]
        audit_payload = {
            'timestamp': time.time(),
            'session_id': session_id,
            'user_id': user_id,
            'query': user_message,
            'answer_source': answer_source,
            'model_used': llm_model_used,
            'recommender_models_used': recommender_models_used,
            'retrieved_count': retrieved_products_count,
            'returned_count': len(rec_products),
            'requested_brand': requested_brand,
            'requested_categories': requested_categories,
            'has_user_context': bool(user_context),
            'has_rec_context': bool(rec_context),
            'is_first_turn': is_first_turn,
            'retrieved_products': retrieved_products_trace,
            'returned_products': returned_products_formatted,
            'trace_sources': trace_sources,
        }
        self._log_ai_audit(audit_payload)
        logger.info(
            "[AI TRACE] session=%s | user=%s | llm=%s | recommender=%s | retrieved=%s | returned=%s",
            session_id,
            user_id or '-',
            llm_model_used,
            ','.join(recommender_models_used),
            retrieved_products_count,
            len(rec_products),
        )

        return {
            'response': ai_response,
            'relevant_products': returned_products_formatted,
            'session_id': session_id,
            'model_used': llm_model_used,
            'recommender_models_used': recommender_models_used,
            'trace': {
                'sources': trace_sources,
                'retrieved_count': retrieved_products_count,
                'retrieved_products': retrieved_products_trace,
                'returned_count': len(rec_products),
                'requested_brand': requested_brand,
                'requested_categories': requested_categories,
                'has_user_context': bool(user_context),
                'has_rec_context': bool(rec_context),
                'is_first_turn': is_first_turn,
            },
            'audit': audit_payload,
        }


def _fmt_product(p, pm):
    return {
        'id': p['id'],
        'name': p['name'],
        'price': p['price'],
        'original_price': p['original_price'],
        'price_formatted': pm.format_price(p['price']),
        'original_price_formatted': pm.format_price(p['original_price']),
        'rating': p['rating'],
        'reviews': p['reviews'],
        'category': p['category'],
        'brand': p['brand'],
        'discount': p['discount'],
        'stock': p['stock'],
        'tags': p.get('tags', []),
        'description': p.get('description', ''),
    }
