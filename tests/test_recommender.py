import numpy as np

import recommender


class DummyRegressor:
    def __init__(self, value):
        self.value = value

    def predict(self, _):
        return np.array([self.value], dtype=np.float32)


def make_recommender_with_loaded_models(loaded):
    rec = recommender.MultiModelRecommender.__new__(recommender.MultiModelRecommender)
    rec._loaded = loaded
    return rec


def test_popularity_top_uses_global_and_category_lists():
    loaded = {
        'm5': {
            'global_top': [
                {'product_id': 1, 'popularity_score': 0.9},
                {'product_id': 2, 'popularity_score': 0.8},
            ],
            'by_category': {
                'Laptop': [
                    {'product_id': 3, 'score': 0.95},
                ]
            },
        }
    }
    rec = make_recommender_with_loaded_models(loaded)

    global_top = rec.popularity_top(top_k=2)
    laptop_top = rec.popularity_top(top_k=2, category='Laptop')

    assert [x['product_id'] for x in global_top] == [1, 2]
    assert [x['product_id'] for x in laptop_top] == [3]


def test_cluster_recommend_and_user_cluster_info():
    loaded = {
        'm6': {
            'uid_cluster': {'U1': 0},
            'cluster_top_products': {'0': [10, 11, 12]},
            'cluster_info': {'0': {'count': 5, 'avg_spend': 100}},
        }
    }
    rec = make_recommender_with_loaded_models(loaded)

    recs = rec.cluster_recommend('U1', top_k=2)
    info = rec.get_user_cluster('U1')

    assert [x['product_id'] for x in recs] == [10, 11]
    assert info['cluster_id'] == 0
    assert info['count'] == 5
    assert rec.cluster_recommend('UNKNOWN', top_k=2) == []


def test_hybrid_recommend_combines_multiple_models_and_excludes_source_product():
    loaded = {
        'm2': {
            1: [
                {'product_id': 2, 'score': 0.9},
                {'product_id': 3, 'score': 0.8},
            ]
        },
        'm3': {
            1: [
                {'product_id': 3, 'score': 0.95},
                {'product_id': 4, 'score': 0.7},
            ]
        },
        'm4': {
            'uid_index': {'U1': 0},
            'user_factors': np.array([[1.0, 0.0]], dtype=np.float32),
            'item_factors': np.array(
                [[0.0, 0.0], [0.6, 0.0], [0.4, 0.0], [0.2, 0.0]], dtype=np.float32
            ),
            'product_ids': [1, 2, 3, 4],
        },
        'm5': {
            'global_top': [
                {'product_id': 4, 'popularity_score': 1.0},
                {'product_id': 2, 'popularity_score': 0.7},
            ],
            'by_category': {},
        },
        'm6': {
            'uid_cluster': {'U1': 1},
            'cluster_top_products': {'1': [2, 4]},
            'cluster_info': {'1': {'count': 2}},
        },
    }
    rec = make_recommender_with_loaded_models(loaded)

    out = rec.hybrid_recommend(user_id='U1', product_id=1, top_k=3)
    ids = [x['product_id'] for x in out]

    assert 1 not in ids
    assert len(out) == 3
    assert ids[0] in {2, 3, 4}


def test_predict_rating_is_clamped_and_has_default():
    loaded = {
        'm7': {
            'feature_names': ['price_m'],
            'model': DummyRegressor(9.7),
            'model_name': 'dummy',
            'mae': 0.1,
            'rmse': 0.2,
        }
    }
    rec = make_recommender_with_loaded_models(loaded)

    assert rec.predict_rating({'price_m': 20}) == 5.0

    rec_no_model = make_recommender_with_loaded_models({})
    assert rec_no_model.predict_rating({'price_m': 20}) == 4.0
