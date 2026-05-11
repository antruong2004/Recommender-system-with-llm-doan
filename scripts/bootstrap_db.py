import argparse
import csv
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.db_service import DBService


def _csv_row_count(path: Path) -> int:
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return max(sum(1 for _ in f) - 1, 0)


def expected_counts(data_dir: Path, source: str) -> dict[str, int]:
    if source == 'json':
        with (data_dir / 'products.json').open('r', encoding='utf-8') as f:
            products = json.load(f)
        with (data_dir / 'users.json').open('r', encoding='utf-8') as f:
            users = json.load(f)
        with (data_dir / 'orders.json').open('r', encoding='utf-8') as f:
            orders = json.load(f)
        return {
            'products': len(products),
            'users': len(users),
            'orders': len(orders),
        }

    csv_dir = data_dir / 'csv'
    return {
        'products': _csv_row_count(csv_dir / 'products.csv'),
        'users': _csv_row_count(csv_dir / 'users.csv'),
        'orders': _csv_row_count(csv_dir / 'orders.csv'),
        'reviews': _csv_row_count(csv_dir / 'reviews_300k.csv'),
        'behavior_logs': _csv_row_count(csv_dir / 'behavior_logs_200k.csv'),
    }


def verify_counts(service: DBService, expected: dict[str, int]) -> bool:
    print('\n[VERIFY] So sanh so dong DB voi file nguon:')
    ok = True
    for table_name, expected_count in expected.items():
        actual_count = service._table_count(table_name)
        status = 'OK' if actual_count == expected_count else 'MISMATCH'
        print(f"  - {table_name}: db={actual_count} expected={expected_count} [{status}]")
        if actual_count != expected_count:
            ok = False
    return ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Bootstrap PostgreSQL data and verify counts.')
    parser.add_argument('--source', choices=['json', 'csv'], default='csv')
    parser.add_argument('--force', action='store_true', help='Force re-import even when table has data.')
    parser.add_argument('--batch-size', type=int, default=5000)
    parser.add_argument('--verify-only', action='store_true', help='Skip import, only verify row counts.')
    parser.add_argument('--data-dir', default=str(ROOT_DIR / 'data'))
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    load_dotenv(ROOT_DIR / '.env')
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('[ERROR] DATABASE_URL is missing in .env')
        return 1

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f'[ERROR] Data directory not found: {data_dir}')
        return 1

    print('[BOOTSTRAP] Init DBService ...')
    service = DBService(db_url)

    if not args.verify_only:
        print(
            f"[BOOTSTRAP] source={args.source} force={args.force} batch_size={args.batch_size} data_dir={data_dir}"
        )
        if args.force:
            print(f"[BOOTSTRAP] Force mode: truncate tables for source={args.source}")
            service.reset_tables_for_source(args.source)
        service.bootstrap(
            data_dir=str(data_dir),
            source=args.source,
            force=args.force,
            batch_size=args.batch_size,
        )
        print('[BOOTSTRAP] Import done')

    expected = expected_counts(data_dir=data_dir, source=args.source)
    is_ok = verify_counts(service=service, expected=expected)

    if is_ok:
        print('\n[RESULT] SUCCESS: Du lieu DB khop voi file nguon')
        return 0

    print('\n[RESULT] FAILED: Co bang khong khop so dong')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
