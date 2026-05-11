import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.db_service import DBService


DATASET_HINTS = {
    'users': ['user', 'customer', 'profile'],
    'products': ['product', 'item', 'catalog'],
    'orders': ['order', 'transaction', 'purchase'],
    'interactions': ['interaction', 'behavior', 'click', 'event', 'view', 'rating', 'review'],
}


def _norm_text(value: Any) -> str:
    text = '' if value is None else str(value)
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ''):
            return default
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ''):
            return default
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _safe_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _csv_files(input_dir: Path) -> list[Path]:
    return sorted([p for p in input_dir.rglob('*') if p.is_file() and p.suffix.lower() == '.csv'])


def _score_columns(columns: list[str], hint: str) -> int:
    cols = {_norm_text(c) for c in columns}
    score = 0
    if hint == 'users':
        score += sum(1 for c in cols if any(k in c for k in ['user', 'customer', 'age', 'gender', 'occupation', 'city']))
    elif hint == 'products':
        score += sum(1 for c in cols if any(k in c for k in ['product', 'item', 'name', 'brand', 'category', 'price', 'rating']))
    elif hint == 'orders':
        score += sum(1 for c in cols if any(k in c for k in ['order', 'purchase', 'transaction', 'date', 'price', 'qty', 'quantity']))
    elif hint == 'interactions':
        score += sum(1 for c in cols if any(k in c for k in ['click', 'view', 'event', 'rating', 'review', 'session', 'timestamp']))
    return score


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def _pick_file(files: list[Path], hint: str) -> Path | None:
    best = None
    best_score = -1
    for file in files:
        try:
            with file.open('r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                cols = reader.fieldnames or []
        except Exception:
            continue
        score = _score_columns(cols, hint)
        if score > best_score:
            best = file
            best_score = score
    return best


def _build_product_payload(rows: list[dict[str, Any]], source_name: str) -> list[dict[str, Any]]:
    products = []
    for idx, row in enumerate(rows, start=1):
        pid = row.get('product_id') or row.get('item_id') or row.get('id') or idx
        name = row.get('product_name') or row.get('name') or row.get('title') or row.get('item_name') or f'Kaggle Product {pid}'
        category = row.get('category') or row.get('product_category') or row.get('type') or 'Unknown'
        brand = row.get('brand') or row.get('manufacturer') or row.get('seller') or 'Kaggle'
        price = row.get('price') or row.get('unit_price') or row.get('sale_price') or row.get('amount') or 0
        rating = row.get('rating') or row.get('score') or 0
        reviews = row.get('reviews') or row.get('review_count') or row.get('rating_count') or 0
        description = row.get('description') or row.get('product_description') or row.get('summary') or ''
        tags = []
        for key in ['tags', 'keywords', 'features']:
            if row.get(key):
                tags.extend([t.strip() for t in re.split(r'[;,|]', str(row[key])) if t.strip()])
        products.append({
            'id': _to_int(pid, idx),
            'name': str(name),
            'category': str(category),
            'brand': str(brand),
            'price': _to_float(price, 0.0),
            'original_price': _to_float(row.get('original_price') or row.get('mrp') or price, 0.0),
            'discount': _to_float(row.get('discount') or row.get('discount_percent') or 0, 0.0),
            'rating': _to_float(rating, 0.0),
            'reviews': _to_int(reviews, 0),
            'stock': _to_int(row.get('stock') or row.get('inventory') or 0, 0),
            'description': str(description),
            'specs': {k: v for k, v in row.items() if k not in {'product_id', 'item_id', 'id', 'name', 'title', 'product_name', 'category', 'product_category', 'type', 'brand', 'manufacturer', 'seller', 'price', 'unit_price', 'sale_price', 'amount', 'rating', 'score', 'reviews', 'review_count', 'rating_count', 'description', 'product_description', 'summary', 'tags', 'keywords', 'features', 'original_price', 'mrp', 'discount', 'discount_percent', 'stock', 'inventory'} and v not in (None, '')},
            'colors': [],
            'tags': list(dict.fromkeys([t.lower() for t in tags]))[:12],
            'source': source_name,
        })
    return products


def _build_user_payload(rows: list[dict[str, Any]], source_name: str) -> list[dict[str, Any]]:
    users = []
    for idx, row in enumerate(rows, start=1):
        uid = row.get('user_id') or row.get('customer_id') or row.get('id') or idx
        name = row.get('name') or row.get('full_name') or row.get('username') or row.get('customer_name') or f'Kaggle User {uid}'
        users.append({
            'user_id': str(uid),
            'name_user': str(name),
            'age': _to_int(row.get('age') or row.get('birth_year') or 0, 0),
            'gender': str(row.get('gender') or row.get('sex') or ''),
            'occupation': str(row.get('occupation') or row.get('job') or row.get('segment') or ''),
            'city': str(row.get('city') or row.get('location') or ''),
            'region': str(row.get('region') or row.get('state') or row.get('country') or ''),
            'registration_date': str(row.get('registration_date') or row.get('signup_date') or row.get('created_at') or ''),
            'source': source_name,
        })
    return users


def _build_order_payload(rows: list[dict[str, Any]], source_name: str) -> list[dict[str, Any]]:
    orders = []
    for idx, row in enumerate(rows, start=1):
        oid = row.get('order_id') or row.get('transaction_id') or row.get('id') or f'KG_ORD_{idx}'
        orders.append({
            'order_id': str(oid),
            'user_id': str(row.get('user_id') or row.get('customer_id') or row.get('buyer_id') or row.get('uid') or ''),
            'product_id': _to_int(row.get('product_id') or row.get('item_id') or row.get('pid') or 0, 0),
            'quantity': _to_int(row.get('quantity') or row.get('qty') or 1, 1),
            'total_price': _to_float(row.get('total_price') or row.get('price') or row.get('amount') or 0, 0.0),
            'date': str(row.get('date') or row.get('order_date') or row.get('timestamp') or row.get('event_time') or ''),
            'status': str(row.get('status') or 'Kaggle'),
            'rating': _to_float(row.get('rating') or row.get('score') or 0, 0.0),
            'review': str(row.get('review') or row.get('review_text') or row.get('comment') or ''),
            'source': source_name,
        })
    return orders


def _build_interaction_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    by_user = defaultdict(set)
    by_product = defaultdict(int)
    for row in rows:
        uid = str(row.get('user_id') or row.get('customer_id') or row.get('buyer_id') or row.get('uid') or '')
        pid = _to_int(row.get('product_id') or row.get('item_id') or row.get('pid') or 0, 0)
        event = _norm_text(row.get('event_type') or row.get('action') or row.get('type') or row.get('behavior') or '')
        counts[event or 'unknown'] += 1
        if uid:
            by_user[uid].add(pid)
        if pid:
            by_product[pid] += 1
    return {
        'event_counts': dict(counts),
        'unique_users': len(by_user),
        'unique_products': len(by_product),
        'top_products': sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:20],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Integrate Kaggle collaborative dataset into the existing pipeline.')
    parser.add_argument('--input-dir', required=True, help='Path to Kaggle dataset folder or extracted CSV folder.')
    parser.add_argument('--output-dir', default=str(ROOT_DIR / 'data' / 'kaggle'), help='Where normalized files will be written.')
    parser.add_argument('--db-url', default=os.getenv('DATABASE_URL', ''), help='Optional PostgreSQL URL to import normalized data.')
    parser.add_argument('--import-db', action='store_true', help='Import normalized data into PostgreSQL as well.')
    parser.add_argument('--source-name', default='kaggle_collab', help='Label stored in normalized payloads.')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = _csv_files(input_dir)
    if not csv_files:
        print(f'[ERROR] No CSV files found in: {input_dir}')
        return 1

    picked_users = _pick_file(csv_files, 'users')
    picked_products = _pick_file(csv_files, 'products')
    picked_orders = _pick_file(csv_files, 'orders')
    picked_interactions = _pick_file(csv_files, 'interactions')

    print('[KAGGLE] Selected files:')
    print(f'  users        : {picked_users}')
    print(f'  products     : {picked_products}')
    print(f'  orders       : {picked_orders}')
    print(f'  interactions : {picked_interactions}')

    products = _build_product_payload(_read_csv(picked_products), args.source_name) if picked_products else []
    users = _build_user_payload(_read_csv(picked_users), args.source_name) if picked_users else []
    orders = _build_order_payload(_read_csv(picked_orders), args.source_name) if picked_orders else []
    interactions = _read_csv(picked_interactions) if picked_interactions else []
    summary = _build_interaction_summary(interactions) if interactions else {}

    (output_dir / 'products.json').write_text(_safe_json(products), encoding='utf-8')
    (output_dir / 'users.json').write_text(_safe_json(users), encoding='utf-8')
    (output_dir / 'orders.json').write_text(_safe_json(orders), encoding='utf-8')
    (output_dir / 'summary.json').write_text(_safe_json(summary), encoding='utf-8')

    print('[KAGGLE] Wrote normalized files:')
    print(f'  - {output_dir / "products.json"}')
    print(f'  - {output_dir / "users.json"}')
    print(f'  - {output_dir / "orders.json"}')
    print(f'  - {output_dir / "summary.json"}')

    if args.import_db:
        if not args.db_url:
            print('[ERROR] --import-db was set but DB url is empty')
            return 2
        service = DBService(args.db_url)
        if products:
            service.upsert_products(products)
        if users:
            service.upsert_users(users)
        if orders:
            service.upsert_orders(orders)
        print('[KAGGLE] Imported normalized data into PostgreSQL')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
