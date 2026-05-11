import csv
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC = ROOT_DIR / 'user_personalized_features.csv'
OUT = ROOT_DIR / 'data' / 'user_personas.json'


def to_bool(value: str) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes', 'y'}


def main() -> int:
    if not SRC.exists():
        print(f'[ERROR] Missing source file: {SRC}')
        return 1

    personas = []
    with SRC.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            personas.append({
                'persona_id': row.get('User_ID') or row.get('user_id') or '',
                'age': int(float(row.get('Age') or 0)),
                'gender': row.get('Gender') or '',
                'location': row.get('Location') or '',
                'income': int(float(row.get('Income') or 0)),
                'interests': row.get('Interests') or '',
                'last_login_days_ago': int(float(row.get('Last_Login_Days_Ago') or 0)),
                'purchase_frequency': int(float(row.get('Purchase_Frequency') or 0)),
                'average_order_value': float(row.get('Average_Order_Value') or 0),
                'total_spending': float(row.get('Total_Spending') or 0),
                'product_category_preference': row.get('Product_Category_Preference') or '',
                'time_spent_on_site_minutes': int(float(row.get('Time_Spent_on_Site_Minutes') or 0)),
                'pages_viewed': int(float(row.get('Pages_Viewed') or 0)),
                'newsletter_subscription': to_bool(row.get('Newsletter_Subscription') or 'false'),
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(personas, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[OK] Wrote {len(personas)} personas -> {OUT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
