"""
╔══════════════════════════════════════════════════════════════════╗
║         TECHSTORE AI - MULTI-MODEL TRAINING PIPELINE            ║
║  Huấn luyện 7 kiểu AI khác nhau trên 400K đơn hàng / 20K SP   ║
╠══════════════════════════════════════════════════════════════════╣
║  Model 1: Semantic Vector Search  (Sentence-Transformers)       ║
║  Model 2: TF-IDF Content-Based    (Cosine Similarity)           ║
║  Model 3: Item-Item CF            (Co-purchase Matrix)          ║
║  Model 4: SVD Matrix Factorization(Latent Factor 50 dims)       ║
║  Model 5: Popularity / Trending   (Time-decayed Scoring)        ║
║  Model 6: User Clustering         (KMeans k=6)                  ║
║  Model 7: Rating Predictor        (Random Forest Regressor)     ║
╚══════════════════════════════════════════════════════════════════╝
Output: models/ folder (sử dụng bởi recommender.py)
"""

import json, os, time, warnings, pickle, math
import numpy as np
import pandas as pd
from datetime import datetime

warnings.filterwarnings('ignore')
np.random.seed(42)

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA   = os.path.join(ROOT, 'data')
MODELS = os.path.join(ROOT, 'models')
os.makedirs(MODELS, exist_ok=True)

# ── Màu terminal ────────────────────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner(title):
    print(f"\n{CYAN}{'='*62}")
    print(f"  {BOLD}{title}{RESET}{CYAN}")
    print(f"{'='*62}{RESET}")

def ok(msg):  print(f"  {GREEN}✔{RESET}  {msg}")
def info(msg): print(f"  {YELLOW}→{RESET}  {msg}")
def err(msg): print(f"  {RED}✘{RESET}  {msg}")

# ════════════════════════════════════════════════════════════
# TẢI DỮ LIỆU
# ════════════════════════════════════════════════════════════
banner("TẢI DỮ LIỆU HỆ THỐNG")

info("Đọc products.json ...")
with open(os.path.join(DATA, 'products.json'), encoding='utf-8') as f:
    products = json.load(f)
ok(f"Sản phẩm: {len(products):,}")

info("Đọc synthetic_400k.csv ...")
df = pd.read_csv(os.path.join(DATA, 'csv', 'synthetic_400k.csv'))
df['date'] = pd.to_datetime(df['date'])
ok(f"Đơn hàng: {len(df):,} | Users: {df['user_id'].nunique():,} | Products: {df['product_id'].nunique():,}")

product_ids = [p['id'] for p in products]
product_map = {p['id']: p for p in products}
pid_to_idx  = {pid: i for i, pid in enumerate(product_ids)}
users_list  = sorted(df['user_id'].unique())
uid_to_idx  = {uid: i for i, uid in enumerate(users_list)}
N_PRODUCTS  = len(products)
N_USERS     = len(users_list)
info(f"N_PRODUCTS={N_PRODUCTS} | N_USERS={N_USERS}")


# ════════════════════════════════════════════════════════════
# MODEL 1 — SEMANTIC VECTOR SEARCH (Sentence-Transformers)
# ════════════════════════════════════════════════════════════
banner("MODEL 1 — SEMANTIC VECTOR SEARCH")
info("Đây là model đã build bằng build_vectors.py")
info("Kiểm tra product_vectors.json ...")

vec_path = os.path.join(DATA, 'product_vectors.json')
if os.path.exists(vec_path):
    with open(vec_path, encoding='utf-8') as f:
        vec_data = json.load(f)
    n_vec = len(vec_data.get('vectors', []))
    dim   = vec_data.get('meta', {}).get('dimension', 0)
    model_name = vec_data.get('meta', {}).get('model', '?')
    ok(f"✓ {n_vec} vectors × {dim}D | model: {model_name}")
    # Save summary để recommender dùng
    json.dump({"status": "ok", "n_vectors": n_vec, "dimension": dim,
               "model": model_name, "path": vec_path},
              open(os.path.join(MODELS, 'm1_semantic_meta.json'), 'w'))
else:
    err("Không tìm thấy product_vectors.json! Chạy build_vectors.py trước.")


# ════════════════════════════════════════════════════════════
# MODEL 2 — TF-IDF CONTENT-BASED FILTERING
# ════════════════════════════════════════════════════════════
banner("MODEL 2 — TF-IDF CONTENT-BASED FILTERING")
t0 = time.time()
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
from scipy import sparse

info("Xây dựng văn bản mô tả sản phẩm ...")
def product_to_doc(p):
    specs = ' '.join(f"{k} {v}" for k, v in p.get('specs', {}).items())
    tags  = ' '.join(p.get('tags', []))
    # Lặp lại category/brand để tăng trọng số
    return (
        f"{p['name']} {p['name']} "
        f"{p['category']} {p['category']} {p['category']} "
        f"{p['brand']} {p['brand']} "
        f"{p.get('description', '')} "
        f"{tags} {tags} "
        f"{specs}"
    )

docs = [product_to_doc(p) for p in products]

info("Fit TF-IDF vectorizer (ngram 1-2, min_df=1) ...")
tfidf = TfidfVectorizer(
    analyzer='word',
    ngram_range=(1, 2),
    min_df=1,
    max_features=8000,
    strip_accents=None,  # Giữ tiếng Việt
)
tfidf_matrix = tfidf.fit_transform(docs)  # (N_PRODUCTS, vocab)
ok(f"TF-IDF matrix: {tfidf_matrix.shape} | vocab: {len(tfidf.vocabulary_):,}")

info("Tính cosine similarity top-20 mỗi sản phẩm (batched) ...")
# Tính từng batch để tránh OOM với 20K×20K
BATCH = 200
m2_topk = {}
for start in range(0, N_PRODUCTS, BATCH):
    end = min(start + BATCH, N_PRODUCTS)
    batch = tfidf_matrix[start:end]
    sim_batch = sk_cosine(batch, tfidf_matrix)  # (BATCH, N_PRODUCTS)
    for local_i in range(sim_batch.shape[0]):
        global_i = start + local_i
        pid = product_ids[global_i]
        row = sim_batch[local_i].copy()
        row[global_i] = -1  # Loại bỏ chính nó
        top_indices = np.argsort(row)[::-1][:20]
        m2_topk[pid] = [
            {"product_id": product_ids[j], "score": float(row[j])}
            for j in top_indices if row[j] > 0.01
        ]
    if start % 2000 == 0:
        info(f"  TF-IDF batch {start}/{N_PRODUCTS}")
ok(f"TF-IDF top-K computed for {len(m2_topk)} products")

with open(os.path.join(MODELS, 'm2_tfidf_topk.json'), 'w', encoding='utf-8') as f:
    json.dump(m2_topk, f, ensure_ascii=False)
# Lưu vectorizer
with open(os.path.join(MODELS, 'm2_tfidf_vectorizer.pkl'), 'wb') as f:
    pickle.dump(tfidf, f)
ok(f"✓ Model 2 lưu xong  [{time.time()-t0:.1f}s]")


# ════════════════════════════════════════════════════════════
# MODEL 3 — ITEM-ITEM COLLABORATIVE FILTERING (Co-purchase)
# ════════════════════════════════════════════════════════════
banner("MODEL 3 — ITEM-ITEM CF (Co-purchase Matrix)")
t0 = time.time()

info("Xây dựng ma trận co-purchase từ 400K đơn hàng ...")
# Nhóm các sản phẩm mỗi user đã mua
user_items = df.groupby('user_id')['product_id'].apply(list).to_dict()

# Build item-item co-count matrix (limit pair explosion per user)
from collections import defaultdict, Counter
import itertools
co_count = defaultdict(Counter)
for uid, item_list in user_items.items():
    unique_items = list(set(item_list))
    # Limit to top 30 items per user to avoid O(n^2) explosion
    if len(unique_items) > 30:
        unique_items = unique_items[:30]
    for a, b in itertools.combinations(unique_items, 2):
        co_count[a][b] += 1
        co_count[b][a] += 1

info(f"Co-count pairs: {sum(len(v) for v in co_count.values()):,}")

# Chuẩn hóa: jaccard-style  sim(a,b) = co(a,b) / (freq(a) + freq(b) - co(a,b))
item_freq = df['product_id'].value_counts().to_dict()
m3_topk = {}
for pid in product_ids:
    freq_a = item_freq.get(pid, 0)
    neighbors = co_count.get(pid, {})
    scores = []
    for other_pid, co in neighbors.items():
        freq_b = item_freq.get(other_pid, 0)
        denom  = freq_a + freq_b - co
        sim    = co / denom if denom > 0 else 0
        scores.append((other_pid, sim))
    scores.sort(key=lambda x: x[1], reverse=True)
    m3_topk[pid] = [
        {"product_id": opid, "score": float(s)}
        for opid, s in scores[:20]
    ]

with open(os.path.join(MODELS, 'm3_item_cf_topk.json'), 'w', encoding='utf-8') as f:
    json.dump(m3_topk, f, ensure_ascii=False)
ok(f"✓ Model 3 lưu xong  [{time.time()-t0:.1f}s]")


# ════════════════════════════════════════════════════════════
# MODEL 4 — SVD MATRIX FACTORIZATION
# ════════════════════════════════════════════════════════════
banner("MODEL 4 — SVD MATRIX FACTORIZATION (k=100 latent)")
t0 = time.time()

info("Xây dựng user-item rating matrix (sparse) ...")
# Aggregated rating: mean rating per (user, product) pair
agg = df.groupby(['user_id', 'product_id'])['rating_order'].mean().reset_index()
agg.columns = ['user_id', 'product_id', 'rating']

# Map to indices
u_idx = agg['user_id'].map(uid_to_idx).values
p_idx = agg['product_id'].map(pid_to_idx).values
ratings_val = agg['rating'].values.astype(np.float32)

R_sparse = sparse.csr_matrix(
    (ratings_val, (u_idx, p_idx)),
    shape=(N_USERS, N_PRODUCTS),
    dtype=np.float32
)
ok(f"User-Item matrix: {R_sparse.shape} | nnz: {R_sparse.nnz:,} | density: {R_sparse.nnz/(N_USERS*N_PRODUCTS)*100:.2f}%")

info("Áp dụng Truncated SVD (k=100) ...")
from sklearn.decomposition import TruncatedSVD

K = 100
svd = TruncatedSVD(n_components=K, random_state=42, n_iter=10)
U50 = svd.fit_transform(R_sparse)           # (N_USERS, K)
Vt50 = svd.components_                      # (K, N_PRODUCTS)
sigma = svd.singular_values_                 # (K,)
explained = svd.explained_variance_ratio_.sum()
ok(f"SVD hoàn thành: U{U50.shape}, Vt{Vt50.shape} | explained variance: {explained*100:.1f}%")

# Tính item embeddings: V = Vt.T * diag(sigma)
item_factors = (Vt50.T * sigma).astype(np.float32)  # (N_PRODUCTS, K)
user_factors = U50.astype(np.float32)                # (N_USERS,    K)

# Global mean rating
global_mean = float(ratings_val.mean())

# Lưu kết quả
np.save(os.path.join(MODELS, 'm4_user_factors.npy'), user_factors)
np.save(os.path.join(MODELS, 'm4_item_factors.npy'), item_factors)
meta4 = {
    "k": K, "n_users": N_USERS, "n_products": N_PRODUCTS,
    "global_mean": global_mean,
    "explained_variance": float(explained),
    "user_ids": users_list,
    "product_ids": product_ids,
}
json.dump(meta4, open(os.path.join(MODELS, 'm4_svd_meta.json'), 'w'))
ok(f"✓ Model 4 lưu xong  [{time.time()-t0:.1f}s]")


# ════════════════════════════════════════════════════════════
# MODEL 5 — POPULARITY / TRENDING MODEL
# ════════════════════════════════════════════════════════════
banner("MODEL 5 — POPULARITY & TRENDING (Time-decay)")
t0 = time.time()

REFERENCE_DATE = df['date'].max()
info(f"Reference date: {REFERENCE_DATE.date()} | time decay halflife = 60 ngày")

# Time-decay weight: w = exp(-lambda * days), halflife = 60 days
HALF_LIFE = 60
decay_lambda = math.log(2) / HALF_LIFE

df['days_ago']     = (REFERENCE_DATE - df['date']).dt.days
df['decay_weight'] = np.exp(-decay_lambda * df['days_ago'])

# Popularity per product
grp = df.groupby('product_id').agg(
    raw_count    = ('order_id', 'count'),
    decay_score  = ('decay_weight', 'sum'),
    avg_rating   = ('rating_order', 'mean'),
    total_revenue= ('total_price', 'sum'),
    return_rate  = ('is_returned', 'mean'),
).reset_index()

# Composite popularity score = 40% decay + 30% rating + 20% log(revenue) + 10% (1-return)
max_decay   = grp['decay_score'].max()
max_revenue = grp['total_revenue'].max()
grp['norm_decay']   = grp['decay_score'] / max_decay
grp['norm_rating']  = (grp['avg_rating'] - 1) / 4          # 1-5 → 0-1
grp['norm_revenue'] = np.log1p(grp['total_revenue']) / np.log1p(max_revenue)
grp['norm_return']  = 1 - grp['return_rate']

grp['popularity_score'] = (
    0.40 * grp['norm_decay'] +
    0.30 * grp['norm_rating'] +
    0.20 * grp['norm_revenue'] +
    0.10 * grp['norm_return']
)

# Trending: ratio recent 30 days vs 31-90 days
recent_30  = df[df['days_ago'] <= 30].groupby('product_id')['order_id'].count()
older_3090 = df[(df['days_ago'] > 30) & (df['days_ago'] <= 90)].groupby('product_id')['order_id'].count()
trending   = (recent_30 / (older_3090 + 1)).rename('trend_ratio')

grp = grp.join(trending, on='product_id', how='left')
grp['trend_ratio'] = grp['trend_ratio'].fillna(0)

# Popularity by category
cat_df = df.copy()
cat_df['cat'] = cat_df['category']
pop_by_cat = (
    cat_df.groupby(['category', 'product_id'])
    .agg(score=('decay_weight', 'sum'))
    .reset_index()
    .sort_values(['category', 'score'], ascending=[True, False])
)
cat_top = pop_by_cat.groupby('category').apply(
    lambda x: x[['product_id', 'score']].head(30).to_dict('records')
).to_dict()

# Build output
popularity_out = {
    "reference_date": str(REFERENCE_DATE.date()),
    "global_top": grp.sort_values('popularity_score', ascending=False)[
        ['product_id','popularity_score','raw_count','avg_rating','trend_ratio']
    ].head(100).to_dict('records'),
    "trending_top": grp.sort_values('trend_ratio', ascending=False)[
        ['product_id','trend_ratio','popularity_score','raw_count']
    ].head(50).to_dict('records'),
    "by_category": cat_top,
}
with open(os.path.join(MODELS, 'm5_popularity.json'), 'w', encoding='utf-8') as f:
    json.dump(popularity_out, f, ensure_ascii=False)
ok(f"✓ Model 5 lưu xong  [{time.time()-t0:.1f}s]")
info(f"  Top 5 phổ biến: {[int(x['product_id']) for x in popularity_out['global_top'][:5]]}")
info(f"  Top 5 trending: {[int(x['product_id']) for x in popularity_out['trending_top'][:5]]}")


# ════════════════════════════════════════════════════════════
# MODEL 6 — USER CLUSTERING (KMeans k=6)
# ════════════════════════════════════════════════════════════
banner("MODEL 6 — USER CLUSTERING (KMeans k=8)")
t0 = time.time()

CATEGORIES = sorted(df['category'].unique())

info("Trích xuất đặc trưng người dùng từ lịch sử mua hàng (vectorized) ...")
# Vectorized approach for 50K users
user_agg = df.groupby('user_id').agg(
    avg_price=('total_price', 'mean'),
    total_spend=('total_price', 'sum'),
    n_orders=('order_id', 'count'),
    avg_rating=('rating_order', 'mean'),
    return_rate=('is_returned', 'mean'),
    avg_discount=('discount', 'mean'),
    n_categories=('category', 'nunique'),
).reset_index()
user_agg['avg_price'] /= 1e6
user_agg['total_spend'] /= 1e6

# Category distribution per user
user_cat = pd.crosstab(df['user_id'], df['category'], normalize='index').reindex(columns=CATEGORIES, fill_value=0)
# Device distribution
user_dev = pd.crosstab(df['user_id'], df['device_type'], normalize='index')
# Payment distribution
user_pay = pd.crosstab(df['user_id'], df['payment_method'], normalize='index')

user_features = []
valid_user_ids = []
for _, row in user_agg.iterrows():
    uid = row['user_id']
    cat_feats = [user_cat.loc[uid].get(c, 0) if uid in user_cat.index else 0 for c in CATEGORIES]
    is_mobile = user_dev.loc[uid].get('Mobile', 0) if uid in user_dev.index else 0
    is_desktop = user_dev.loc[uid].get('Desktop', 0) if uid in user_dev.index else 0
    uses_cod = user_pay.loc[uid].get('COD', 0) if uid in user_pay.index else 0
    uses_card = user_pay.loc[uid].get('Thẻ tín dụng', 0) if uid in user_pay.index else 0
    feat_row = [row['avg_price'], row['total_spend'], row['n_orders'], row['avg_rating'],
                row['return_rate'], row['avg_discount'], row['n_categories'],
                is_mobile, is_desktop, uses_cod, uses_card] + cat_feats
    user_features.append(feat_row)
    valid_user_ids.append(uid)
if False:  # disabled old loop
    pass  # old per-user loop removed, vectorized above

X_users = np.array(user_features, dtype=np.float32)
ok(f"Feature matrix: {X_users.shape}")

info("Chuẩn hóa + KMeans k=8 ...")
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

scaler  = StandardScaler()
X_scaled = scaler.fit_transform(X_users)

kmeans = KMeans(n_clusters=8, random_state=42, n_init=20, max_iter=500)
labels = kmeans.fit_predict(X_scaled)
ok(f"KMeans hoàn thành | inertia: {kmeans.inertia_:.0f}")

# Phân tích từng cluster
cluster_info = {}
for c in range(8):
    mask = labels == c
    c_uids = [valid_user_ids[i] for i in range(len(valid_user_ids)) if mask[i]]
    c_df   = df[df['user_id'].isin(c_uids)]
    top_cats   = c_df['category'].value_counts().head(3).to_dict()
    top_brands = c_df['brand'].value_counts().head(3).to_dict()
    cluster_info[str(c)] = {
        "count": int(mask.sum()),
        "avg_spend_per_order(triệu)": round(float(X_users[mask, 0].mean()), 2),
        "avg_total_spend(triệu)": round(float(X_users[mask, 1].mean()), 2),
        "avg_orders": round(float(X_users[mask, 2].mean()), 1),
        "avg_rating": round(float(X_users[mask, 3].mean()), 2),
        "top_categories": list(top_cats.keys()),
        "top_brands": list(top_brands.keys()),
    }
    info(f"  Cluster {c}: {mask.sum()} users | avg_spend: {X_users[mask,0].mean():.1f}tr | cats: {list(top_cats.keys())[:2]}")

# Lưu user → cluster mapping
uid_cluster = {uid: int(labels[i]) for i, uid in enumerate(valid_user_ids)}

# Top products per cluster (từ orders)
cluster_top_products = {}
for c in range(8):
    c_uids = [uid for uid, cl in uid_cluster.items() if cl == c]
    c_df   = df[df['user_id'].isin(c_uids)]
    top_pids = c_df['product_id'].value_counts().head(30).index.tolist()
    cluster_top_products[str(c)] = [int(p) for p in top_pids]

m6_out = {
    "cluster_info": cluster_info,
    "uid_cluster": uid_cluster,
    "cluster_top_products": cluster_top_products,
}
with open(os.path.join(MODELS, 'm6_clusters.json'), 'w', encoding='utf-8') as f:
    json.dump(m6_out, f, ensure_ascii=False)

with open(os.path.join(MODELS, 'm6_kmeans.pkl'), 'wb') as f:
    pickle.dump({'scaler': scaler, 'kmeans': kmeans, 'categories': CATEGORIES}, f)
ok(f"✓ Model 6 lưu xong  [{time.time()-t0:.1f}s]")


# ════════════════════════════════════════════════════════════
# MODEL 7 — RATING PREDICTOR (Random Forest Regressor)
# ════════════════════════════════════════════════════════════
banner("MODEL 7 — RATING PREDICTOR (Random Forest)")
t0 = time.time()

info("Xây dựng features cho bài toán dự đoán rating ...")
# Features cho mỗi đơn hàng
cat_dummies   = pd.get_dummies(df['category'], prefix='cat').astype(np.float32)
pay_dummies   = pd.get_dummies(df['payment_method'], prefix='pay').astype(np.float32)
ship_dummies  = pd.get_dummies(df['shipping_method'], prefix='ship').astype(np.float32)
dev_dummies   = pd.get_dummies(df['device_type'], prefix='dev').astype(np.float32)
gender_dummies= pd.get_dummies(df['gender'], prefix='gen').astype(np.float32)

features_df = pd.concat([
    (df['total_price'] / 1e6).rename('price_m'),
    (df['discount']   / 100 ).rename('discount_rate'),
    df['quantity'].rename('quantity'),
    (df['delivery_days']).rename('delivery_days'),
    df['age'].rename('age'),
    (df['rating_product']).rename('product_rating'),
    cat_dummies, pay_dummies, ship_dummies, dev_dummies, gender_dummies,
], axis=1).fillna(0)

y = df['rating_order'].values

ok(f"Feature dimension: {features_df.shape[1]} | samples: {len(y):,}")

info("Train/Test split 80/20 ...")
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

X = features_df.values.astype(np.float32)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
ok(f"Train: {len(X_train):,} | Test: {len(X_test):,}")

info("Huấn luyện Random Forest (100 cây, n_jobs=-1) ...")
rf = RandomForestRegressor(
    n_estimators=100,
    max_depth=8,
    min_samples_leaf=50,
    n_jobs=-1,
    random_state=42,
)
rf.fit(X_train, y_train)

y_pred_rf = rf.predict(X_test)
mae_rf  = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
ok(f"RandomForest → MAE: {mae_rf:.4f} | RMSE: {rmse_rf:.4f}")

info("Huấn luyện Gradient Boosting (100 cây) ...")
gb = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    subsample=0.8,
    random_state=42,
)
gb.fit(X_train, y_train)

y_pred_gb = gb.predict(X_test)
mae_gb  = mean_absolute_error(y_test, y_pred_gb)
rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
ok(f"GradientBoosting → MAE: {mae_gb:.4f} | RMSE: {rmse_gb:.4f}")

# Chọn model tốt hơn
best_model = rf if mae_rf <= mae_gb else gb
best_name  = "RandomForest" if mae_rf <= mae_gb else "GradientBoosting"
ok(f"Best model: {best_name}")

# Feature importance
feature_names = features_df.columns.tolist()
importances   = best_model.feature_importances_
top10_feats   = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
info("Top 10 features quan trọng:")
for fname, imp in top10_feats:
    print(f"     {fname:25s}  {imp*100:.2f}%")

with open(os.path.join(MODELS, 'm7_rating_predictor.pkl'), 'wb') as f:
    pickle.dump({
        'model': best_model,
        'model_name': best_name,
        'feature_names': feature_names,
        'mae': float(mae_rf if mae_rf <= mae_gb else mae_gb),
        'rmse': float(rmse_rf if mae_rf <= mae_gb else rmse_gb),
    }, f)
ok(f"✓ Model 7 lưu xong  [{time.time()-t0:.1f}s]")


# ════════════════════════════════════════════════════════════
# TỔNG KẾT
# ════════════════════════════════════════════════════════════
banner("TỔNG KẾT - TẤT CẢ MODELS ĐÃ ĐƯỢC HUẤN LUYỆN")

files = os.listdir(MODELS)
total_size = sum(os.path.getsize(os.path.join(MODELS, f)) for f in files)
print(f"""
  {GREEN}✔{RESET}  Model 1 — Semantic Vector (sentence-transformers)  → product_vectors.json
  {GREEN}✔{RESET}  Model 2 — TF-IDF Content-Based                     → m2_tfidf_topk.json
  {GREEN}✔{RESET}  Model 3 — Item-Item CF (Co-purchase)               → m3_item_cf_topk.json
  {GREEN}✔{RESET}  Model 4 — SVD Matrix Factorization (k=100)         → m4_*.npy / m4_svd_meta.json
  {GREEN}✔{RESET}  Model 5 — Popularity & Trending                    → m5_popularity.json
  {GREEN}✔{RESET}  Model 6 — User Clustering (KMeans k=8)             → m6_clusters.json
  {GREEN}✔{RESET}  Model 7 — Rating Predictor (RandomForest/GB)       → m7_rating_predictor.pkl

  {CYAN}Thư mục:{RESET} {MODELS}
  {CYAN}Files:  {RESET} {len(files)} files | {total_size/1e6:.1f} MB tổng
""")
info("Chạy tiếp: python recommender.py để kiểm tra inference")
