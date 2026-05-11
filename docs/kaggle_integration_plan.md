# Kaggle Integration Plan

## Mục tiêu
Dùng dataset `kartikeybartwal/ecommerce-product-recommendation-collaborative` như nguồn phụ để tăng chất lượng recommendation, trong khi catalog tiếng Việt hiện tại vẫn là nguồn chính cho chatbot và UI.

## Phương án tích hợp
1. Giữ `data/products.json`, `data/users.json`, `data/orders.json` của project làm catalog chính.
2. Chuẩn hóa dataset Kaggle sang cùng cấu trúc đầu ra:
   - `products.json`
   - `users.json`
   - `orders.json`
   - `summary.json`
3. Đưa dữ liệu normalized vào `data/kaggle/`.
4. Khi train recommender, dùng:
   - catalog hiện tại để render UI/chat
   - Kaggle data để tăng tín hiệu collaborative filtering

## Schema mục tiêu
### Product
- `id`
- `name`
- `category`
- `brand`
- `price`
- `original_price`
- `discount`
- `rating`
- `reviews`
- `stock`
- `description`
- `specs`
- `tags`
- `source`

### User
- `user_id`
- `name_user`
- `age`
- `gender`
- `occupation`
- `city`
- `region`
- `registration_date`
- `source`

### Order / Interaction
- `order_id`
- `user_id`
- `product_id`
- `quantity`
- `total_price`
- `date`
- `status`
- `rating`
- `review`
- `source`

## Script
`scripts/integrate_kaggle_collab.py`

Chức năng:
- tự tìm file CSV phù hợp trong thư mục Kaggle đã giải nén
- chuẩn hóa dữ liệu theo schema trên
- xuất JSON normalized
- có thể import trực tiếp vào PostgreSQL nếu bật `--import-db`

## Cách chạy
```bash
python scripts/integrate_kaggle_collab.py --input-dir "D:\path\to\kaggle_dataset" --output-dir "data\kaggle"
```

Nếu muốn import DB:
```bash
python scripts/integrate_kaggle_collab.py --input-dir "D:\path\to\kaggle_dataset" --output-dir "data\kaggle" --import-db --db-url "postgresql://..."
```
