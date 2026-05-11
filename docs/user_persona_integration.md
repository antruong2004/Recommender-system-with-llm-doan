# User Persona Integration

Dataset: `user_personalized_features.csv`

## Mục đích
Dùng dataset này làm nguồn phụ để xây hồ sơ người dùng (persona) phục vụ:
- cá nhân hóa prompt
- ưu tiên category theo sở thích
- gợi ý theo khả năng chi tiêu
- phân nhóm user theo hành vi mua sắm

## Schema đầu ra
File output:
- `data/user_personas.json`

Mỗi persona có:
- `persona_id`
- `age`
- `gender`
- `location`
- `income`
- `interests`
- `last_login_days_ago`
- `purchase_frequency`
- `average_order_value`
- `total_spending`
- `product_category_preference`
- `time_spent_on_site_minutes`
- `pages_viewed`
- `newsletter_subscription`

## Script import
`scripts/import_user_personalized_features.py`

## Cách chạy
```bash
python scripts/import_user_personalized_features.py
```

## Cách dùng trong project
- dùng để enrich profile của user trong prompt
- làm tín hiệu cho rule-based filtering
- hỗ trợ tạo dashboard insight về nhóm khách hàng
