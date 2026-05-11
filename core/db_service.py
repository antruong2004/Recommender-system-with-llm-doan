import os
import csv
import json
from datetime import datetime

import psycopg
from psycopg.rows import dict_row


class DBService:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._init_schema()

    def _get_conn(self):
        return psycopg.connect(self.db_url, row_factory=dict_row)

    def _init_schema(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id BIGINT PRIMARY KEY,
                    name TEXT,
                    category TEXT,
                    brand TEXT,
                    price REAL,
                    rating REAL,
                    reviews INTEGER,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    product_id BIGINT,
                    category TEXT,
                    date TEXT,
                    rating REAL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id BIGSERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    product_id BIGINT,
                    rating REAL,
                    review_date TEXT,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS behavior_logs (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_id TEXT,
                    action_type TEXT,
                    product_id BIGINT,
                    event_time TEXT,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS answer_audit_logs (
                    log_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    source TEXT,
                    model_used TEXT,
                    answer_source TEXT,
                    trace TEXT NOT NULL,
                    retrieved_count INTEGER,
                    returned_count INTEGER,
                    confidence REAL,
                    is_match INTEGER,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chat_session_time ON chat_messages(session_id, id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_answer_audit_session_time ON answer_audit_logs(session_id, created_at)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_behavior_user ON behavior_logs(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_behavior_action ON behavior_logs(action_type)")
            conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS category TEXT")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_date_category ON orders(date, category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_product_rating ON reviews(product_id, rating)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_behavior_user_action_time ON behavior_logs(user_id, action_type, event_time)"
            )

    @staticmethod
    def _to_int(value, default: int = 0) -> int:
        if value in (None, ''):
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _to_float(value, default: float = 0.0) -> float:
        if value in (None, ''):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _table_count(self, table_name: str) -> int:
        with self._get_conn() as conn:
            row = conn.execute(f"SELECT COUNT(*) AS c FROM {table_name}").fetchone()
            return int(row['c']) if row else 0

    def get_table_counts(self, table_names: list[str] | None = None) -> dict[str, int]:
        names = table_names or ['products', 'users', 'orders', 'reviews', 'behavior_logs', 'chat_messages']
        return {name: self._table_count(name) for name in names}

    @staticmethod
    def _progress_log(table_name: str, processed: int):
        print(f"  [DB][{table_name}] processed={processed}")

    def bootstrap(self, data_dir: str, source: str = 'csv', force: bool = False, batch_size: int = 5000):
        source_normalized = (source or '').strip().lower()
        if source_normalized == 'json':
            self.bootstrap_from_json(data_dir=data_dir, force=force)
            return
        if source_normalized == 'csv':
            self.bootstrap_from_csv(data_dir=data_dir, force=force, batch_size=batch_size)
            return
        raise ValueError("source must be 'json' or 'csv'")

    def reset_tables_for_source(self, source: str):
        source_normalized = (source or '').strip().lower()
        if source_normalized == 'json':
            tables = ['orders', 'users', 'products']
        elif source_normalized == 'csv':
            tables = ['behavior_logs', 'reviews', 'orders', 'users', 'products']
        else:
            raise ValueError("source must be 'json' or 'csv'")

        with self._get_conn() as conn:
            conn.execute(f"TRUNCATE TABLE {', '.join(tables)}")

    def bootstrap_from_json(self, data_dir: str, force: bool = False):
        products_path = os.path.join(data_dir, 'products.json')
        users_path = os.path.join(data_dir, 'users.json')
        orders_path = os.path.join(data_dir, 'orders.json')

        if force or self._table_count('products') == 0:
            with open(products_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            self.upsert_products(products)

        if force or self._table_count('users') == 0:
            with open(users_path, 'r', encoding='utf-8') as f:
                users = json.load(f)
            self.upsert_users(users)

        if force or self._table_count('orders') == 0:
            with open(orders_path, 'r', encoding='utf-8') as f:
                orders = json.load(f)
            self.upsert_orders(orders)

    def bootstrap_from_csv(self, data_dir: str, force: bool = False, batch_size: int = 5000):
        csv_dir = os.path.join(data_dir, 'csv')
        products_path = os.path.join(csv_dir, 'products.csv')
        users_path = os.path.join(csv_dir, 'users.csv')
        orders_path = os.path.join(csv_dir, 'orders.csv')
        reviews_path = os.path.join(csv_dir, 'reviews_300k.csv')
        behavior_logs_path = os.path.join(csv_dir, 'behavior_logs_200k.csv')

        if force or self._table_count('products') == 0:
            with open(products_path, 'r', encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f))
            self.upsert_products(rows)

        if force or self._table_count('users') == 0:
            with open(users_path, 'r', encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f))
            self.upsert_users(rows)

        if force or self._table_count('orders') == 0:
            self._upsert_orders_csv(orders_path, batch_size=batch_size)

        if force or self._table_count('reviews') == 0:
            self._upsert_reviews_csv(reviews_path, batch_size=batch_size)

        if force or self._table_count('behavior_logs') == 0:
            self._upsert_behavior_logs_csv(behavior_logs_path, batch_size=batch_size)

    def _upsert_orders_csv(self, csv_path: str, batch_size: int = 5000):
        sql = """
            INSERT INTO orders(order_id, user_id, product_id, category, date, rating, payload)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                product_id = EXCLUDED.product_id,
                category = EXCLUDED.category,
                date = EXCLUDED.date,
                rating = EXCLUDED.rating,
                payload = EXCLUDED.payload
        """

        with self._get_conn() as conn:
            with conn.cursor() as cur:
                batch = []
                idx = 0
                with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader, start=1):
                        order_id = row.get('order_id') or f"AUTO_{idx}"
                        batch.append(
                            (
                                str(order_id),
                                row.get('user_id'),
                                self._to_int(row.get('product_id'), 0),
                                row.get('category'),
                                row.get('date'),
                                self._to_float(row.get('rating_order'), 0.0),
                                json.dumps(row, ensure_ascii=False),
                            )
                        )
                        if len(batch) >= batch_size:
                            cur.executemany(sql, batch)
                            batch.clear()
                            self._progress_log('orders', idx)
                if batch:
                    cur.executemany(sql, batch)
                    self._progress_log('orders', idx)

    def _upsert_reviews_csv(self, csv_path: str, batch_size: int = 5000):
        sql = """
            INSERT INTO reviews(review_id, user_id, product_id, rating, review_date, payload)
            VALUES(%s, %s, %s, %s, %s, %s)
            ON CONFLICT (review_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                product_id = EXCLUDED.product_id,
                rating = EXCLUDED.rating,
                review_date = EXCLUDED.review_date,
                payload = EXCLUDED.payload
        """

        with self._get_conn() as conn:
            with conn.cursor() as cur:
                batch = []
                idx = 0
                with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader, start=1):
                        review_id = row.get('review_id') or f"REV_AUTO_{idx}"
                        batch.append(
                            (
                                str(review_id),
                                row.get('user_id'),
                                self._to_int(row.get('product_id'), 0),
                                self._to_float(row.get('rating'), 0.0),
                                row.get('review_date'),
                                json.dumps(row, ensure_ascii=False),
                            )
                        )
                        if len(batch) >= batch_size:
                            cur.executemany(sql, batch)
                            batch.clear()
                            self._progress_log('reviews', idx)
                if batch:
                    cur.executemany(sql, batch)
                    self._progress_log('reviews', idx)

    def _upsert_behavior_logs_csv(self, csv_path: str, batch_size: int = 5000):
        sql = """
            INSERT INTO behavior_logs(log_id, user_id, session_id, action_type, product_id, event_time, payload)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (log_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                session_id = EXCLUDED.session_id,
                action_type = EXCLUDED.action_type,
                product_id = EXCLUDED.product_id,
                event_time = EXCLUDED.event_time,
                payload = EXCLUDED.payload
        """

        with self._get_conn() as conn:
            with conn.cursor() as cur:
                batch = []
                idx = 0
                with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader, start=1):
                        log_id = row.get('log_id') or f"LOG_AUTO_{idx}"
                        batch.append(
                            (
                                str(log_id),
                                row.get('user_id'),
                                row.get('session_id'),
                                row.get('action_type'),
                                self._to_int(row.get('product_id'), 0),
                                row.get('timestamp'),
                                json.dumps(row, ensure_ascii=False),
                            )
                        )
                        if len(batch) >= batch_size:
                            cur.executemany(sql, batch)
                            batch.clear()
                            self._progress_log('behavior_logs', idx)
                if batch:
                    cur.executemany(sql, batch)
                    self._progress_log('behavior_logs', idx)

    def upsert_products(self, products: list[dict]):
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO products(id, name, category, brand, price, rating, reviews, payload)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        category = EXCLUDED.category,
                        brand = EXCLUDED.brand,
                        price = EXCLUDED.price,
                        rating = EXCLUDED.rating,
                        reviews = EXCLUDED.reviews,
                        payload = EXCLUDED.payload
                    """,
                    [
                        (
                            int(p['id']),
                            p.get('name'),
                            p.get('category'),
                            p.get('brand'),
                            float(p.get('price', 0) or 0),
                            float(p.get('rating', 0) or 0),
                            int(p.get('reviews', 0) or 0),
                            json.dumps(p, ensure_ascii=False),
                        )
                        for p in products
                        if p.get('id') is not None
                    ],
                )

    def upsert_users(self, users: list[dict]):
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO users(user_id, payload)
                    VALUES(%s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        payload = EXCLUDED.payload
                    """,
                    [
                        (str(u['user_id']), json.dumps(u, ensure_ascii=False))
                        for u in users
                        if u.get('user_id')
                    ],
                )

    def upsert_orders(self, orders: list[dict]):
        rows = []
        for idx, o in enumerate(orders, start=1):
            order_id = o.get('order_id') or f"AUTO_{idx}"
            rows.append(
                (
                    str(order_id),
                    o.get('user_id'),
                    o.get('product_id'),
                    o.get('category'),
                    o.get('date'),
                    float(o.get('rating', 0) or 0),
                    json.dumps(o, ensure_ascii=False),
                )
            )

        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO orders(order_id, user_id, product_id, category, date, rating, payload)
                    VALUES(%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (order_id) DO UPDATE SET
                        user_id = EXCLUDED.user_id,
                        product_id = EXCLUDED.product_id,
                        category = EXCLUDED.category,
                        date = EXCLUDED.date,
                        rating = EXCLUDED.rating,
                        payload = EXCLUDED.payload
                    """,
                    rows,
                )

    def get_products(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT payload FROM products ORDER BY id").fetchall()
        return [json.loads(r['payload']) for r in rows]

    def get_users(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT payload FROM users ORDER BY user_id").fetchall()
        return [json.loads(r['payload']) for r in rows]

    def get_orders(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT payload FROM orders ORDER BY order_id").fetchall()
        return [json.loads(r['payload']) for r in rows]

    def save_chat_message(self, session_id: str, role: str, content: str, user_id: str | None = None):
        created_at = datetime.utcnow()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages(session_id, user_id, role, content, created_at)
                VALUES(%s, %s, %s, %s, %s)
                """,
                (session_id, user_id, role, content, created_at),
            )

    def save_answer_audit(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        *,
        user_id: str | None = None,
        source: str | None = None,
        model_used: str | None = None,
        answer_source: str | None = None,
        trace: dict | None = None,
        retrieved_count: int = 0,
        returned_count: int = 0,
        confidence: float | None = None,
        is_match: bool | None = None,
        log_id: str | None = None,
    ):
        created_at = datetime.utcnow()
        payload = json.dumps(
            {
                'session_id': session_id,
                'user_id': user_id,
                'user_message': user_message,
                'ai_response': ai_response,
                'source': source,
                'model_used': model_used,
                'answer_source': answer_source,
                'trace': trace or {},
                'retrieved_count': retrieved_count,
                'returned_count': returned_count,
                'confidence': confidence,
                'is_match': is_match,
                'created_at': created_at.isoformat(),
            },
            ensure_ascii=False,
        )
        log_id = log_id or f"AUDIT_{int(created_at.timestamp() * 1000)}"
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO answer_audit_logs(
                    log_id, session_id, user_id, user_message, ai_response,
                    source, model_used, answer_source, trace,
                    retrieved_count, returned_count, confidence, is_match, created_at
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (log_id) DO UPDATE SET
                    session_id = EXCLUDED.session_id,
                    user_id = EXCLUDED.user_id,
                    user_message = EXCLUDED.user_message,
                    ai_response = EXCLUDED.ai_response,
                    source = EXCLUDED.source,
                    model_used = EXCLUDED.model_used,
                    answer_source = EXCLUDED.answer_source,
                    trace = EXCLUDED.trace,
                    retrieved_count = EXCLUDED.retrieved_count,
                    returned_count = EXCLUDED.returned_count,
                    confidence = EXCLUDED.confidence,
                    is_match = EXCLUDED.is_match,
                    created_at = EXCLUDED.created_at
                """,
                (
                    log_id,
                    session_id,
                    user_id,
                    user_message,
                    ai_response,
                    source,
                    model_used,
                    answer_source,
                    payload,
                    int(retrieved_count or 0),
                    int(returned_count or 0),
                    confidence,
                    1 if is_match else 0 if is_match is not None else None,
                    created_at,
                ),
            )

    def get_chat_history(self, session_id: str, limit: int = 100):
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY id DESC
                LIMIT %s
                """,
                (session_id, limit),
            ).fetchall()
        rows = list(reversed(rows))
        return [
            {
                'role': r['role'],
                'content': r['content'],
                'created_at': r['created_at'],
            }
            for r in rows
        ]

    def clear_chat_history(self, session_id: str):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = %s", (session_id,))
