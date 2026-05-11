# ============================================================
# BUILD_VECTORS.PY
# Tao vector embeddings cho san pham su dung Sentence-Transformers
# Mo hinh: paraphrase-multilingual-MiniLM-L12-v2 (ho tro tieng Viet)
# Output : data/product_vectors.json
# ============================================================

import json
import os
import time
import numpy as np
from sentence_transformers import SentenceTransformer

# ---- Config ------------------------------------------------
MODEL_NAME  = 'paraphrase-multilingual-MiniLM-L12-v2'
DATA_DIR    = os.path.join(os.path.dirname(__file__), 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
OUTPUT_FILE   = os.path.join(DATA_DIR, 'product_vectors.json')

# ---- Helper ------------------------------------------------
def product_to_sentence(p: dict) -> str:
    """Chuyen san pham thanh cau van giau noi dung de embedding."""
    specs_parts = [f"{k} {v}" for k, v in p.get('specs', {}).items()]
    parts = [
        p['name'],
        p['category'],
        p['brand'],
        p.get('description', ''),
        ' '.join(p.get('tags', [])),
        ' '.join(specs_parts),
    ]
    return ' | '.join(filter(None, parts))


def cosine_similarity(a: list, b: list) -> float:
    """Tinh cosine similarity giua hai vector."""
    va = np.array(a)
    vb = np.array(b)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(np.dot(va, vb) / denom) if denom > 0 else 0.0


# ---- Main --------------------------------------------------
def main():
    print("=" * 60)
    print("  TechStore AI - Vector Builder")
    print(f"  Mo hinh: {MODEL_NAME}")
    print("=" * 60)

    # 1. Tai du lieu san pham
    print("\n[1] Dang tai products.json ...")
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)
    print(f"    -> {len(products)} san pham")

    # 2. Load model
    print(f"\n[2] Dang tai SentenceTransformer [{MODEL_NAME}] ...")
    print("    (Co the mat 1-2 phut neu chua co cache)")
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME)
    print(f"    -> Hoan thanh trong {time.time()-t0:.1f}s")

    # 3. Tao sentences
    print("\n[3] Xay dung van ban mo ta san pham ...")
    sentences = []
    for p in products:
        sent = product_to_sentence(p)
        sentences.append(sent)
        print(f"    ID {p['id']:>3}: {sent[:80]}...")

    # 4. Encode
    print(f"\n[4] Dang encoding {len(sentences)} san pham ...")
    t0 = time.time()
    embeddings = model.encode(sentences, show_progress_bar=True, normalize_embeddings=True)
    print(f"    -> Hoan thanh trong {time.time()-t0:.1f}s")
    print(f"    -> Kich thuoc embedding: {embeddings.shape[1]} chieu")

    # 5. Luu ket qua
    print(f"\n[5] Luu ket qua vao {OUTPUT_FILE} ...")
    output = {
        "meta": {
            "model":      MODEL_NAME,
            "dimension":  int(embeddings.shape[1]),
            "num_products": len(products),
            "normalized": True,
            "built_at":   time.strftime('%Y-%m-%d %H:%M:%S'),
        },
        "vectors": []
    }
    for p, sent, emb in zip(products, sentences, embeddings):
        output["vectors"].append({
            "product_id":  p['id'],
            "name":        p['name'],
            "category":    p['category'],
            "brand":       p['brand'],
            "price":       p['price'],
            "text":        sent,
            "embedding":   emb.tolist(),
        })

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"    -> Da luu {len(output['vectors'])} vectors")

    # 6. Kiem tra nhanh
    print("\n[6] Kiem tra thu (cosine similarity):")
    test_pairs = [
        (0, 1, "San pham 1 vs 2"),
        (0, 5, "Dien thoai vs Laptop"),
    ]
    for i, j, label in test_pairs:
        sim = cosine_similarity(output['vectors'][i]['embedding'],
                                output['vectors'][j]['embedding'])
        p1 = output['vectors'][i]['name']
        p2 = output['vectors'][j]['name']
        print(f"    {label}: {p1[:25]} <-> {p2[:25]} = {sim:.4f}")

    print("\n" + "=" * 60)
    print(f"  HOAN THANH!  {OUTPUT_FILE}")
    print(f"  {len(products)} vectors, {int(embeddings.shape[1])} chieu")
    print("=" * 60)


if __name__ == '__main__':
    main()
