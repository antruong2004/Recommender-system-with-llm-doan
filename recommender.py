"""
╔══════════════════════════════════════════════════════════════════╗
║          TECHSTORE AI — MULTI-MODEL RECOMMENDER                 ║
║  7 kiểu AI kết hợp để đưa ra gợi ý sản phẩm tối ưu             ║
╚══════════════════════════════════════════════════════════════════╝
Sử dụng trong app.py: from recommender import MultiModelRecommender
"""

import json, os, pickle, time
import numpy as np
from typing import Optional

ROOT   = os.path.dirname(os.path.abspath(__file__))
DATA   = os.path.join(ROOT, 'data')
MODELS = os.path.join(ROOT, 'models')


class MultiModelRecommender:
    """
    Hệ thống gợi ý kết hợp 7 model AI.
    Chỉ load file, không cần dữ liệu gốc khi inference.
    """

    def __init__(self):
        self._loaded = {}
        self._load_all()

    # ───────────────────────────────────────────────
    # LOAD TẤT CẢ MODELS
    # ───────────────────────────────────────────────
    def _load_all(self):
        t0 = time.time()
        print("[Recommender] Đang tải các models AI ...")

        # M1: Vector Search → đã trong VectorSearchEngine ở app.py, chỉ note metadata
        m1_path = os.path.join(MODELS, 'm1_semantic_meta.json')
        if os.path.exists(m1_path):
            with open(m1_path, encoding='utf-8') as f:
                self._loaded['m1'] = json.load(f)
            print(f"  [M1] Semantic Vector OK — {self._loaded['m1']['n_vectors']} vectors")

        # M2: TF-IDF top-K
        m2_path = os.path.join(MODELS, 'm2_tfidf_topk.json')
        if os.path.exists(m2_path):
            with open(m2_path, encoding='utf-8') as f:
                raw = json.load(f)
            # Convert keys to int
            self._loaded['m2'] = {int(k): v for k, v in raw.items()}
            print(f"  [M2] TF-IDF Content-Based OK — {len(self._loaded['m2'])} sản phẩm")

        # M3: Item-Item CF
        m3_path = os.path.join(MODELS, 'm3_item_cf_topk.json')
        if os.path.exists(m3_path):
            with open(m3_path, encoding='utf-8') as f:
                raw = json.load(f)
            self._loaded['m3'] = {int(k): v for k, v in raw.items()}
            print(f"  [M3] Item-Item CF OK — {len(self._loaded['m3'])} sản phẩm")

        # M4: SVD
        m4_meta = os.path.join(MODELS, 'm4_svd_meta.json')
        m4_user = os.path.join(MODELS, 'm4_user_factors.npy')
        m4_item = os.path.join(MODELS, 'm4_item_factors.npy')
        if all(os.path.exists(p) for p in [m4_meta, m4_user, m4_item]):
            with open(m4_meta, encoding='utf-8') as f:
                meta = json.load(f)
            self._loaded['m4'] = {
                'meta': meta,
                'user_factors': np.load(m4_user),   # (N_USERS, K)
                'item_factors': np.load(m4_item),   # (N_PRODUCTS, K)
                'uid_index': {uid: i for i, uid in enumerate(meta['user_ids'])},
                'pid_index': {pid: i for i, pid in enumerate(meta['product_ids'])},
                'product_ids': meta['product_ids'],
            }
            print(f"  [M4] SVD OK — U{self._loaded['m4']['user_factors'].shape} V{self._loaded['m4']['item_factors'].shape}")

        # M5: Popularity
        m5_path = os.path.join(MODELS, 'm5_popularity.json')
        if os.path.exists(m5_path):
            with open(m5_path, encoding='utf-8') as f:
                raw = json.load(f)
            # Convert product_id keys to int
            self._loaded['m5'] = raw
            # Build fast-lookup dict
            self._loaded['m5_scores'] = {
                int(item['product_id']): item['popularity_score']
                for item in raw['global_top']
            }
            print(f"  [M5] Popularity OK — {len(raw['global_top'])} top products")

        # M6: User Clustering
        m6_path = os.path.join(MODELS, 'm6_clusters.json')
        if os.path.exists(m6_path):
            with open(m6_path, encoding='utf-8') as f:
                raw = json.load(f)
            self._loaded['m6'] = raw
            print(f"  [M6] User Clustering OK — {len(raw['cluster_info'])} clusters")

        # M7: Rating Predictor
        m7_path = os.path.join(MODELS, 'm7_rating_predictor.pkl')
        if os.path.exists(m7_path):
            with open(m7_path, 'rb') as f:
                data = pickle.load(f)
            self._loaded['m7'] = data
            print(f"  [M7] Rating Predictor OK — {data['model_name']} (MAE={data['mae']:.4f})")

        print(f"[Recommender] ✓ Tải xong {len(self._loaded)} models trong {time.time()-t0:.1f}s\n")

    # ───────────────────────────────────────────────
    # MODEL 2: TF-IDF Content-Based
    # ───────────────────────────────────────────────
    def tfidf_similar(self, product_id: int, top_k: int = 10) -> list:
        """Trả về top-K sản phẩm tương tự theo TF-IDF."""
        if 'm2' not in self._loaded:
            return []
        items = self._loaded['m2'].get(product_id, [])
        return [{'product_id': int(x['product_id']), 'score': x['score'],
                 'method': 'tfidf'} for x in items[:top_k]]

    # ───────────────────────────────────────────────
    # MODEL 3: Item-Item CF
    # ───────────────────────────────────────────────
    def item_cf_similar(self, product_id: int, top_k: int = 10) -> list:
        """Trả về top-K sản phẩm thường được mua cùng."""
        if 'm3' not in self._loaded:
            return []
        items = self._loaded['m3'].get(product_id, [])
        return [{'product_id': int(x['product_id']), 'score': x['score'],
                 'method': 'item_cf'} for x in items[:top_k]]

    # ───────────────────────────────────────────────
    # MODEL 4: SVD — Predict ratings for user
    # ───────────────────────────────────────────────
    def svd_recommend(self, user_id: str, top_k: int = 10,
                       exclude_ids: Optional[list] = None) -> list:
        """SVD Matrix Factorization: dự đoán rating cho user."""
        if 'm4' not in self._loaded:
            return []
        m4 = self._loaded['m4']
        u_idx = m4['uid_index'].get(user_id)
        if u_idx is None:
            return []
        u_vec = m4['user_factors'][u_idx]         # (K,)
        scores = m4['item_factors'] @ u_vec        # (N_PRODUCTS,)
        exclude_set = set(exclude_ids or [])
        product_scores = [
            (int(m4['product_ids'][i]), float(scores[i]))
            for i in range(len(scores))
            if m4['product_ids'][i] not in exclude_set
        ]
        product_scores.sort(key=lambda x: x[1], reverse=True)
        return [{'product_id': pid, 'score': s, 'method': 'svd'}
                for pid, s in product_scores[:top_k]]

    def svd_similar(self, user_id: str, top_k: int = 10, exclude_ids: Optional[list] = None) -> list:
        """Alias tương thích với các endpoint/dashboard đang gọi svd_similar."""
        return self.svd_recommend(user_id=user_id, top_k=top_k, exclude_ids=exclude_ids)

    # ───────────────────────────────────────────────
    # MODEL 5: Popularity
    # ───────────────────────────────────────────────
    def popularity_top(self, top_k: int = 10, category: Optional[str] = None) -> list:
        """Trả về sản phẩm phổ biến nhất (có thể lọc theo danh mục)."""
        if 'm5' not in self._loaded:
            return []
        m5 = self._loaded['m5']
        if category and category in m5.get('by_category', {}):
            items = m5['by_category'][category]
            return [{'product_id': int(x['product_id']), 'score': float(x['score']),
                     'method': 'popularity'} for x in items[:top_k]]
        items = m5['global_top']
        return [{'product_id': int(x['product_id']),
                 'score': float(x['popularity_score']),
                 'method': 'popularity'} for x in items[:top_k]]

    def trending_top(self, top_k: int = 10) -> list:
        """Trả về sản phẩm đang trending (tăng trưởng gần đây)."""
        if 'm5' not in self._loaded:
            return []
        items = self._loaded['m5'].get('trending_top', [])
        return [{'product_id': int(x['product_id']),
                 'score': float(x['trend_ratio']),
                 'method': 'trending'} for x in items[:top_k]]

    # ───────────────────────────────────────────────
    # MODEL 6: Cluster-Based
    # ───────────────────────────────────────────────
    def cluster_recommend(self, user_id: str, top_k: int = 10) -> list:
        """Gợi ý dựa trên cluster người dùng."""
        if 'm6' not in self._loaded:
            return []
        m6 = self._loaded['m6']
        cluster_id = m6['uid_cluster'].get(user_id)
        if cluster_id is None:
            return []
        top_pids = m6['cluster_top_products'].get(str(cluster_id), [])
        return [{'product_id': int(pid), 'score': 1.0 - rank/len(top_pids),
                 'method': 'cluster', 'cluster': cluster_id}
                for rank, pid in enumerate(top_pids[:top_k])]

    def get_user_cluster(self, user_id: str) -> Optional[dict]:
        """Trả về thông tin cluster của user."""
        if 'm6' not in self._loaded:
            return None
        m6 = self._loaded['m6']
        cid = m6['uid_cluster'].get(user_id)
        if cid is None:
            return None
        return {'cluster_id': cid, **m6['cluster_info'].get(str(cid), {})}

    # ───────────────────────────────────────────────
    # MODEL 7: Rating Prediction
    # ───────────────────────────────────────────────
    def predict_rating(self, features: dict) -> float:
        """
        Dự đoán rating dựa trên đặc trưng đơn hàng.
        features: dict với keys như price_m, discount_rate, category, etc.
        """
        if 'm7' not in self._loaded:
            return 4.0
        m7 = self._loaded['m7']
        feat_names = m7['feature_names']
        x = np.zeros(len(feat_names), dtype=np.float32)
        for i, fname in enumerate(feat_names):
            x[i] = float(features.get(fname, 0))
        pred = m7['model'].predict(x.reshape(1, -1))[0]
        return float(np.clip(pred, 1.0, 5.0))

    # ───────────────────────────────────────────────
    # HYBRID ENSEMBLE (kết hợp tất cả)
    # ───────────────────────────────────────────────
    def hybrid_recommend(
        self,
        user_id: Optional[str] = None,
        product_id: Optional[int] = None,
        category:   Optional[str] = None,
        top_k: int = 12,
        weights: Optional[dict] = None,
    ) -> list:
        """
        Kết hợp tất cả 7 model với trọng số.
        
        Weights mặc định:
          semantic (m1) = 0.30  ← dùng qua vector_engine ở app.py
          tfidf    (m2) = 0.15
          item_cf  (m3) = 0.20
          svd      (m4) = 0.15
          pop      (m5) = 0.10
          cluster  (m6) = 0.10
        """
        W = weights or {
            'm2': 0.15, 'm3': 0.20, 'm4': 0.15,
            'm5': 0.10, 'm6': 0.10,
        }

        # Thu thập tất cả candidates
        all_scores: dict = {}  # pid → weighted_score

        def add_scores(items, weight, cap=1.0):
            if not items:
                return
            max_s = max(x['score'] for x in items) or 1.0
            for x in items:
                pid = x['product_id']
                norm_score = (x['score'] / max_s) * cap
                all_scores[pid] = all_scores.get(pid, 0) + weight * norm_score

        # M2: TF-IDF (nếu có product_id)
        if product_id:
            add_scores(self.tfidf_similar(product_id, 30), W.get('m2', 0))

        # M3: Item CF (nếu có product_id)
        if product_id:
            add_scores(self.item_cf_similar(product_id, 30), W.get('m3', 0))

        # M4: SVD (nếu có user_id)
        if user_id:
            add_scores(self.svd_recommend(user_id, 30), W.get('m4', 0))

        # M5: Popularity
        add_scores(self.popularity_top(30, category=category), W.get('m5', 0))

        # M6: Cluster
        if user_id:
            add_scores(self.cluster_recommend(user_id, 30), W.get('m6', 0))

        # Loại bỏ product_id gốc
        if product_id and product_id in all_scores:
            del all_scores[product_id]

        # Sắp xếp và trả về
        ranked = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        return [{'product_id': pid, 'hybrid_score': round(score, 4)}
                for pid, score in ranked[:top_k]]

    # ───────────────────────────────────────────────
    # THÔNG TIN MODEL
    # ───────────────────────────────────────────────
    def model_info(self) -> dict:
        info = {}
        if 'm1' in self._loaded:
            info['m1_semantic'] = self._loaded['m1']
        if 'm2' in self._loaded:
            info['m2_tfidf'] = {'n_products': len(self._loaded['m2'])}
        if 'm3' in self._loaded:
            info['m3_item_cf'] = {'n_products': len(self._loaded['m3'])}
        if 'm4' in self._loaded:
            m = self._loaded['m4']['meta']
            info['m4_svd'] = {'k': m['k'], 'n_users': m['n_users'],
                               'explained_variance': round(m['explained_variance'], 4)}
        if 'm5' in self._loaded:
            info['m5_popularity'] = {
                'n_global_top': len(self._loaded['m5']['global_top']),
                'reference_date': self._loaded['m5']['reference_date'],
            }
        if 'm6' in self._loaded:
            info['m6_clustering'] = {
                'n_clusters': len(self._loaded['m6']['cluster_info']),
                'cluster_sizes': {k: v['count']
                                  for k, v in self._loaded['m6']['cluster_info'].items()},
            }
        if 'm7' in self._loaded:
            info['m7_rating_pred'] = {
                'model': self._loaded['m7']['model_name'],
                'mae':   round(self._loaded['m7']['mae'], 4),
                'rmse':  round(self._loaded['m7']['rmse'], 4),
            }
        return info


# ── Singleton toàn cục ────────────────────────────────────────
_INSTANCE: Optional[MultiModelRecommender] = None

def get_recommender() -> MultiModelRecommender:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = MultiModelRecommender()
    return _INSTANCE


# ── CLI test ─────────────────────────────────────────────────
if __name__ == '__main__':
    rec = get_recommender()
    print("\n" + "="*60)
    print("  MODEL INFO")
    print("="*60)
    for k, v in rec.model_info().items():
        print(f"  {k}: {v}")

    print("\n" + "="*60)
    print("  TEST RECOMMENDATIONS")
    print("="*60)

    # Test TF-IDF
    print("\n[M2] TF-IDF similar to product_id=1 (iPhone 15 Pro Max):")
    for r in rec.tfidf_similar(1, top_k=5):
        print(f"   pid={r['product_id']:4d}  score={r['score']:.4f}")

    # Test Item CF  
    print("\n[M3] Item-CF similar to product_id=1:")
    for r in rec.item_cf_similar(1, top_k=5):
        print(f"   pid={r['product_id']:4d}  score={r['score']:.4f}")

    # Test SVD
    print("\n[M4] SVD recommendations for user SU000001:")
    for r in rec.svd_recommend('SU000001', top_k=5):
        print(f"   pid={r['product_id']:4d}  score={r['score']:.4f}")

    # Test Popularity
    print("\n[M5] Top 5 phổ biến nhất:")
    for r in rec.popularity_top(top_k=5):
        print(f"   pid={r['product_id']:4d}  score={r['score']:.4f}")

    # Test Trending
    print("\n[M5] Top 5 Trending:")
    for r in rec.trending_top(top_k=5):
        print(f"   pid={r['product_id']:4d}  trend={r['score']:.4f}")

    # Test Cluster
    print("\n[M6] Cluster của SU000001:", rec.get_user_cluster('SU000001'))
    print("[M6] Cluster-based recs for SU000001:")
    for r in rec.cluster_recommend('SU000001', top_k=5):
        print(f"   pid={r['product_id']:4d}  score={r['score']:.4f}  cluster={r['cluster']}")

    # Test Hybrid
    print("\n[HYBRID] Kết hợp tất cả models (user=SU000001, product=1):")
    for r in rec.hybrid_recommend(user_id='SU000001', product_id=1, top_k=8):
        print(f"   pid={r['product_id']:4d}  hybrid={r['hybrid_score']:.4f}")
