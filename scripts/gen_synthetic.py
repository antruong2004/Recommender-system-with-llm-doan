"""
Enterprise-grade synthetic data generator for TechStore AI.
Generates 200K orders with realistic e-commerce features.
"""
import json, random, os, math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

DATA_DIR = 'd:/ok/data'

# ─── Load real products ───────────────────────────────────────────────────────
with open(f'{DATA_DIR}/products.json', encoding='utf-8') as f:
    products_raw = json.load(f)
product_ids = [p['id'] for p in products_raw]
product_map = {p['id']: p for p in products_raw}
print(f"✅ Loaded {len(products_raw)} products (IDs: {min(product_ids)}-{max(product_ids)})")

# ─── Build 2000 synthetic users ───────────────────────────────────────────────
OCCUPATIONS = [
    ("Sinh viên CNTT", "Nam", (18, 24)),
    ("Sinh viên đại học", "Nữ", (18, 23)),
    ("Lập trình viên", "Nam", (22, 35)),
    ("Lập trình viên Frontend", "Nữ", (22, 32)),
    ("Kỹ sư phần mềm", "Nam", (24, 38)),
    ("Data Scientist", "Nam", (24, 35)),
    ("DevOps Engineer", "Nam", (25, 38)),
    ("Game thủ chuyên nghiệp", "Nam", (18, 30)),
    ("Streamer / Youtuber", "Nam", (20, 32)),
    ("Content Creator", "Nữ", (20, 30)),
    ("Nhân viên văn phòng", "Nữ", (23, 40)),
    ("Kế toán", "Nữ", (24, 42)),
    ("Nhân viên ngân hàng", "Nữ", (24, 38)),
    ("Nhân viên HR", "Nữ", (22, 35)),
    ("Marketing Manager", "Nữ", (26, 42)),
    ("Doanh nhân", "Nam", (28, 50)),
    ("CEO Startup", "Nam", (28, 45)),
    ("Giám đốc sản xuất", "Nam", (35, 55)),
    ("Kiến trúc sư", "Nam", (28, 48)),
    ("Kỹ sư xây dựng", "Nam", (25, 45)),
    ("Kỹ sư điện tử", "Nam", (24, 40)),
    ("Giáo viên", "Nam", (27, 55)),
    ("Giáo viên cấp 3", "Nữ", (25, 52)),
    ("Bác sĩ", "Nữ", (28, 50)),
    ("Bác sĩ nha khoa", "Nữ", (27, 48)),
    ("Bác sĩ dinh dưỡng", "Nữ", (26, 45)),
    ("Nhà thiết kế đồ họa", "Nữ", (22, 38)),
    ("Product Designer", "Nữ", (24, 38)),
    ("Nhà báo", "Nữ", (24, 40)),
    ("Nhà văn / Blogger", "Nam", (24, 45)),
    ("Nhà nhiếp ảnh", "Nam", (24, 45)),
    ("Nhạc sĩ / Producer", "Nam", (22, 40)),
    ("Sinh viên Kiến trúc", "Nam", (19, 25)),
    ("Sinh viên Y khoa", "Nữ", (19, 26)),
    ("Sinh viên Ngoại thương", "Nữ", (19, 24)),
    ("Sinh viên game thủ", "Nam", (19, 24)),
    ("Sinh viên Tài chính", "Nam", (19, 24)),
    ("Sinh viên Mỹ thuật", "Nữ", (19, 24)),
    ("Stylist / Fashion Blogger", "Nữ", (22, 35)),
    ("Nhân viên tự do", "Nam", (22, 40)),
]

MALE_SURNAMES = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Vũ','Đặng','Bùi','Lý','Đỗ','Hồ','Trương','Ngô','Đinh','Lưu','Hà','Đào','Dương','Phan','Tô']
MALE_MIDNAMES = ['Văn','Minh','Đức','Trọng','Công','Hữu','Duy','Tiến','Quốc','Gia','Thanh','Tuấn','Anh','Hùng','Khoa','Phú']
MALE_NAMES = ['An','Hùng','Dũng','Cường','Phát','Giang','Khoa','Khánh','Luận','Minh','Nghĩa','Phúc','Quân','Sơn','Tân','Uy','Việt','Nhật','Long','Lâm']
FEMALE_SURNAMES = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Vũ','Đặng','Bùi','Lý','Đỗ','Hồ','Trương','Ngô','Đinh','Phan','Lưu']
FEMALE_MIDNAMES = ['Thị','Ngọc','Lan','Thu','Mai','Thanh','Hồng','Bảo','Diễm','Quỳnh','Phương','Thùy','Kim']
FEMALE_NAMES = ['An','Bình','Chi','Dung','Em','Giang','Hoa','Lan','Linh','Ly','My','Ngân','Như','Oanh','Phương','Quỳnh','Tâm','Thanh','Thảo','Vy','Yến']

def gen_name(gender):
    if gender == 'Nam':
        return f"{random.choice(MALE_SURNAMES)} {random.choice(MALE_MIDNAMES)} {random.choice(MALE_NAMES)}"
    else:
        return f"{random.choice(FEMALE_SURNAMES)} {random.choice(FEMALE_MIDNAMES)} {random.choice(FEMALE_NAMES)}"

# ─── THÀNH PHỐ với trọng số dân số ──────────────────────────────────────────
CITIES = [
    ("TP. Hồ Chí Minh", "Miền Nam", 30),
    ("Hà Nội", "Miền Bắc", 25),
    ("Đà Nẵng", "Miền Trung", 8),
    ("Hải Phòng", "Miền Bắc", 5),
    ("Cần Thơ", "Miền Nam", 4),
    ("Biên Hòa", "Miền Nam", 3),
    ("Nha Trang", "Miền Trung", 3),
    ("Huế", "Miền Trung", 3),
    ("Buôn Ma Thuột", "Miền Trung", 2),
    ("Vũng Tàu", "Miền Nam", 2),
    ("Thái Nguyên", "Miền Bắc", 2),
    ("Nam Định", "Miền Bắc", 2),
    ("Vinh", "Miền Trung", 2),
    ("Quy Nhơn", "Miền Trung", 2),
    ("Long Xuyên", "Miền Nam", 1),
    ("Bắc Ninh", "Miền Bắc", 1),
    ("Thanh Hóa", "Miền Bắc", 1),
    ("Đà Lạt", "Miền Trung", 1),
    ("Phan Thiết", "Miền Trung", 1),
    ("Rạch Giá", "Miền Nam", 1),
    ("Pleiku", "Miền Trung", 1),
]
CITY_NAMES = [c[0] for c in CITIES]
CITY_REGIONS = {c[0]: c[1] for c in CITIES}
CITY_WEIGHTS = [c[2] for c in CITIES]

# ─── Generate users ──────────────────────────────────────────────────────────
N_USERS = 2000
users = []
occ_cycle = OCCUPATIONS * (N_USERS // len(OCCUPATIONS) + 1)
random.shuffle(occ_cycle)
for i in range(N_USERS):
    uid = f"SU{i+1:04d}"
    occ, gender, age_range = occ_cycle[i]
    age = random.randint(age_range[0], age_range[1])
    name = gen_name(gender)
    city = random.choices(CITY_NAMES, weights=CITY_WEIGHTS)[0]
    region = CITY_REGIONS[city]
    # Registration date: 6 months before first potential order
    reg_date = datetime(2022, 6, 1) + timedelta(days=random.randint(0, 365))
    users.append({
        'user_id': uid, 'name_user': name, 'age': age, 'gender': gender,
        'occupation': occ, 'city': city, 'region': region,
        'registration_date': reg_date.strftime('%Y-%m-%d'),
    })

df_users_syn = pd.DataFrame(users)
print(f"✅ Generated {N_USERS} users across {df_users_syn['city'].nunique()} cities")

# ─── Occupation preference map ───────────────────────────────────────────────
cat_products = {}
for p in products_raw:
    cat_products.setdefault(p['category'], [])
    cat_products[p['category']].append(p['id'])

OCC_PREF = {
    "Sinh viên CNTT":         {'cats': ['Điện thoại','Laptop','Phụ kiện','Lưu trữ','Màn hình'], 'budget': (3e6,25e6)},
    "Sinh viên đại học":      {'cats': ['Điện thoại','Máy tính bảng','Phụ kiện'], 'budget': (2e6,15e6)},
    "Lập trình viên":         {'cats': ['Laptop','Màn hình','Phụ kiện','Lưu trữ'], 'budget': (5e6,50e6)},
    "Lập trình viên Frontend":{'cats': ['Laptop','Màn hình','Phụ kiện'], 'budget': (5e6,45e6)},
    "Kỹ sư phần mềm":        {'cats': ['Laptop','Màn hình','Lưu trữ','Phụ kiện'], 'budget': (5e6,60e6)},
    "Data Scientist":         {'cats': ['Laptop','Màn hình','Lưu trữ'], 'budget': (8e6,80e6)},
    "DevOps Engineer":        {'cats': ['Laptop','Màn hình','Lưu trữ','Phụ kiện'], 'budget': (5e6,50e6)},
    "Game thủ chuyên nghiệp": {'cats': ['Laptop','Điện thoại','Phụ kiện','Màn hình'], 'budget': (5e6,60e6)},
    "Streamer / Youtuber":    {'cats': ['Phụ kiện','Điện thoại','Màn hình','Máy ảnh'], 'budget': (5e6,50e6)},
    "Content Creator":        {'cats': ['Máy ảnh','Phụ kiện','Điện thoại'], 'budget': (5e6,45e6)},
    "Nhân viên văn phòng":    {'cats': ['Điện thoại','Laptop','Phụ kiện','Đồng hồ thông minh'], 'budget': (3e6,25e6)},
    "Kế toán":                {'cats': ['Laptop','Màn hình','Phụ kiện'], 'budget': (3e6,25e6)},
    "Nhân viên ngân hàng":    {'cats': ['Điện thoại','Laptop','Đồng hồ thông minh'], 'budget': (5e6,35e6)},
    "Nhân viên HR":           {'cats': ['Điện thoại','Đồng hồ thông minh','Phụ kiện'], 'budget': (3e6,25e6)},
    "Marketing Manager":      {'cats': ['Điện thoại','Laptop','Phụ kiện','Màn hình'], 'budget': (5e6,40e6)},
    "Doanh nhân":             {'cats': ['Điện thoại','Laptop','Đồng hồ thông minh','Màn hình'], 'budget': (10e6,80e6)},
    "CEO Startup":            {'cats': ['Điện thoại','Laptop','Đồng hồ thông minh'], 'budget': (15e6,100e6)},
    "Giám đốc sản xuất":     {'cats': ['Laptop','Điện thoại','Đồng hồ thông minh'], 'budget': (10e6,60e6)},
    "Kiến trúc sư":           {'cats': ['Laptop','Màn hình','Máy ảnh','Phụ kiện'], 'budget': (8e6,60e6)},
    "Kỹ sư xây dựng":        {'cats': ['Điện thoại','Đồng hồ thông minh','Laptop'], 'budget': (4e6,30e6)},
    "Kỹ sư điện tử":         {'cats': ['Laptop','Màn hình','Lưu trữ','Phụ kiện'], 'budget': (4e6,35e6)},
    "Giáo viên":              {'cats': ['Laptop','Phụ kiện','Điện thoại','Màn hình'], 'budget': (3e6,25e6)},
    "Giáo viên cấp 3":       {'cats': ['Laptop','Phụ kiện','Điện thoại'], 'budget': (3e6,22e6)},
    "Bác sĩ":                {'cats': ['Điện thoại','Đồng hồ thông minh','Laptop'], 'budget': (4e6,35e6)},
    "Bác sĩ nha khoa":       {'cats': ['Điện thoại','Đồng hồ thông minh','Máy tính bảng'], 'budget': (5e6,35e6)},
    "Bác sĩ dinh dưỡng":     {'cats': ['Đồng hồ thông minh','Máy tính bảng','Điện thoại'], 'budget': (4e6,30e6)},
    "Nhà thiết kế đồ họa":   {'cats': ['Màn hình','Laptop','Máy tính bảng','Máy ảnh'], 'budget': (5e6,50e6)},
    "Product Designer":       {'cats': ['Laptop','Màn hình','Máy tính bảng'], 'budget': (6e6,50e6)},
    "Nhà báo":                {'cats': ['Laptop','Điện thoại','Phụ kiện','Máy ảnh'], 'budget': (5e6,35e6)},
    "Nhà văn / Blogger":      {'cats': ['Laptop','Phụ kiện','Đồng hồ thông minh'], 'budget': (5e6,35e6)},
    "Nhà nhiếp ảnh":          {'cats': ['Máy ảnh','Phụ kiện','Lưu trữ','Màn hình'], 'budget': (5e6,60e6)},
    "Nhạc sĩ / Producer":    {'cats': ['Phụ kiện','Laptop','Màn hình'], 'budget': (5e6,45e6)},
    "Sinh viên Kiến trúc":   {'cats': ['Laptop','Màn hình','Phụ kiện'], 'budget': (3e6,35e6)},
    "Sinh viên Y khoa":       {'cats': ['Laptop','Điện thoại','Máy tính bảng'], 'budget': (2e6,20e6)},
    "Sinh viên Ngoại thương": {'cats': ['Điện thoại','Laptop','Đồng hồ thông minh'], 'budget': (2e6,18e6)},
    "Sinh viên game thủ":    {'cats': ['Laptop','Điện thoại','Phụ kiện','Màn hình'], 'budget': (2e6,25e6)},
    "Sinh viên Tài chính":   {'cats': ['Điện thoại','Laptop','Phụ kiện'], 'budget': (2e6,18e6)},
    "Sinh viên Mỹ thuật":    {'cats': ['Máy tính bảng','Màn hình','Phụ kiện','Laptop'], 'budget': (2e6,25e6)},
    "Stylist / Fashion Blogger": {'cats': ['Điện thoại','Đồng hồ thông minh','Phụ kiện'], 'budget': (3e6,25e6)},
    "Nhân viên tự do":       {'cats': ['Điện thoại','Laptop','Phụ kiện'], 'budget': (2e6,20e6)},
}

def get_pref_products(occupation):
    pref = OCC_PREF.get(occupation, {'cats': list(cat_products.keys()), 'budget': (2e6, 40e6)})
    pref_ids = []
    for cat in pref['cats']:
        pref_ids.extend(cat_products.get(cat, []))
    bmin, bmax = pref['budget']
    pref_ids_filtered = [pid for pid in pref_ids 
                         if bmin * 0.2 <= product_map[pid]['price'] <= bmax * 2.5]
    if not pref_ids_filtered:
        pref_ids_filtered = product_ids[:]
    # Ensure ALL product_ids can appear (small chance for non-preferred)
    return pref_ids_filtered

# ─── Ensure coverage: force every product to have a min number of orders ─────
# Build a guaranteed pool: at least 100 orders per product
guaranteed_orders = []
for pid in product_ids:
    for _ in range(100):
        guaranteed_orders.append(pid)
random.shuffle(guaranteed_orders)

# ─── Reviews ─────────────────────────────────────────────────────────────────
REVIEW_TEMPLATES = {
    5: [
        "Sản phẩm tuyệt vời, rất hài lòng! Chất lượng vượt kỳ vọng.",
        "Chất lượng xuất sắc, đúng như mô tả. Giao hàng nhanh.",
        "Giao hàng nhanh, sản phẩm chính hãng. 10/10!",
        "Rất đáng tiền, sẽ mua lại. Recommend cho mọi người!",
        "Mua lần 2 rồi vẫn tốt, chất lượng đảm bảo. Shop uy tín.",
        "Đóng gói cẩn thận, sản phẩm hoàn hảo. Sẽ giới thiệu bạn bè.",
        "Sử dụng rất tốt, hiệu năng cao. Xứng đáng với giá tiền.",
        "Giao trước hẹn, hàng đẹp, đúng mô tả. Cảm ơn shop!",
    ],
    4: [
        "Sản phẩm tốt, giao hàng ổn. Hài lòng với đơn hàng này.",
        "Dùng được, đáng đồng tiền. Sẽ giới thiệu bạn bè.",
        "Tương đối ổn, nhưng pin hơi yếu hơn kỳ vọng một chút.",
        "Khá ưng ý, thiết kế đẹp. Chức năng như mô tả.",
        "Chất lượng tốt so với mức giá. Giao hàng đúng hạn.",
        "Sản phẩm như mô tả, đóng gói kỹ. Chỉ hơi lâu giao.",
        "Tạm hài lòng, sẽ cân nhắc mua thêm sản phẩm khác.",
    ],
    3: [
        "Bình thường, không quá nổi bật so với giá tiền.",
        "Tạm ổn, nhưng giá hơi cao so với chất lượng nhận được.",
        "Dùng được nhưng không như kỳ vọng. Cần cải thiện thêm.",
        "Chấp nhận được, vẫn dùng tốt nhưng không ấn tượng.",
        "Trung bình, giao hàng hơi chậm. Sản phẩm tạm OK.",
    ],
    2: [
        "Hơi thất vọng so với kỳ vọng. Chất lượng chưa tương xứng giá.",
        "Giao hàng chậm, sản phẩm tạm. Cần cải thiện dịch vụ.",
        "Chất lượng không tốt bằng ảnh và mô tả. Hơi tiếc.",
        "Sản phẩm bị trầy nhẹ khi nhận. Đóng gói chưa tốt.",
    ],
    1: [
        "Sản phẩm kém chất lượng, rất không hài lòng.",
        "Không đúng mô tả, thất vọng hoàn toàn. Muốn đổi trả.",
        "Hàng lỗi, đã liên hệ đổi trả. Trải nghiệm rất tệ.",
    ]
}

# ─── Payment methods ─────────────────────────────────────────────────────────
PAYMENT_METHODS = ['COD', 'Thẻ tín dụng', 'Ví MoMo', 'Ví ZaloPay', 'Chuyển khoản ngân hàng', 'VNPay']
# Age-based payment preference: young => e-wallet, old => COD/bank
def get_payment(age, total_price):
    if age < 25:
        weights = [15, 10, 30, 25, 5, 15]   # young: MoMo/ZaloPay dominant
    elif age < 35:
        weights = [10, 20, 25, 15, 10, 20]   # mid: mixed
    elif age < 45:
        weights = [20, 25, 10, 8, 25, 12]    # older: credit card/bank
    else:
        weights = [30, 20, 5, 3, 30, 12]     # senior: COD/bank
    # High value orders: more credit card / bank transfer
    if total_price > 20e6:
        weights[1] += 15  # credit card
        weights[4] += 10  # bank transfer
        weights[0] -= 10  # less COD
    return random.choices(PAYMENT_METHODS, weights=weights)[0]

# ─── Device types ─────────────────────────────────────────────────────────────
DEVICE_TYPES = ['Mobile', 'Desktop', 'Tablet']
def get_device(age, occupation):
    if age < 30:
        weights = [65, 25, 10]  # young: mostly mobile
    elif age < 45:
        weights = [45, 40, 15]  # mid: more desktop
    else:
        weights = [35, 45, 20]  # older: desktop/tablet
    # Occupation adjustments
    if 'Lập trình' in occupation or 'Kỹ sư' in occupation or 'DevOps' in occupation or 'Data' in occupation:
        weights = [30, 60, 10]  # tech workers: desktop
    if 'Sinh viên' in occupation:
        weights = [70, 20, 10]  # students: mobile
    return random.choices(DEVICE_TYPES, weights=weights)[0]

# ─── Coupon codes ─────────────────────────────────────────────────────────────
COUPONS = [None]*60 + ['WELCOME10']*8 + ['FLASH20']*5 + ['TET2024']*4 + \
          ['SUMMER15']*5 + ['LOYAL30']*3 + ['TECH10']*5 + ['NEWUSER']*5 + \
          ['FREESHIP']*5

COUPON_DISCOUNT = {
    None: 0, 'WELCOME10': 10, 'FLASH20': 20, 'TET2024': 15,
    'SUMMER15': 15, 'LOYAL30': 30, 'TECH10': 10, 'NEWUSER': 10, 'FREESHIP': 0
}

# ─── Shipping methods ────────────────────────────────────────────────────────
SHIPPING_METHODS = ['Tiêu chuẩn', 'Nhanh', 'Hỏa tốc', 'Tiết kiệm']
SHIPPING_FEES = {'Tiêu chuẩn': 30000, 'Nhanh': 50000, 'Hỏa tốc': 80000, 'Tiết kiệm': 15000}
SHIPPING_DAYS = {'Tiêu chuẩn': (3, 5), 'Nhanh': (1, 3), 'Hỏa tốc': (1, 1), 'Tiết kiệm': (5, 8)}

# ─── Generate 100K orders ────────────────────────────────────────────────────
N_ORDERS = 200_000
STATUSES = ['Đã giao'] * 70 + ['Đang giao'] * 12 + ['Chờ xử lý'] * 8 + \
           ['Đã hủy'] * 5 + ['Đã hoàn trả'] * 3 + ['Đang xử lý hoàn trả'] * 2

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 11, 30)
date_range_days = (end_date - start_date).days

def date_weight(d):
    m = d.month
    if m in [1, 2]:   return 1.6   # Tết
    if m in [11, 12]: return 1.9   # Q4 cuối năm / Black Friday / Noel
    if m in [6, 7]:   return 1.3   # hè
    if m in [3]:      return 1.2   # 8/3
    if m in [10]:     return 1.1   # 20/10
    return 1.0

# Track per-user orders for customer_type calculation
user_order_count = {u['user_id']: 0 for u in users}

orders = []
order_counter = 1
guaranteed_idx = 0  # index into guaranteed_orders pool

print(f"\nGenerating {N_ORDERS:,} orders...")
for i in range(N_ORDERS):
    if i % 20000 == 0:
        print(f"  {i:,}/{N_ORDERS:,}...")

    user = users[random.randint(0, N_USERS - 1)]
    uid = user['user_id']
    occ = user['occupation']
    age = user['age']

    # Pick product: use guaranteed pool first, then preference-based
    if guaranteed_idx < len(guaranteed_orders):
        product_id = guaranteed_orders[guaranteed_idx]
        guaranteed_idx += 1
    else:
        pref_pids = get_pref_products(occ)
        product_id = random.choice(pref_pids)

    p = product_map[product_id]

    # Quantity: 1 (most), 2 (some), 3 (rare)
    quantity = random.choices([1, 2, 3], weights=[78, 17, 5])[0]

    # Discount from product itself
    base_discount = p.get('discount', 0)

    # Coupon
    coupon = random.choice(COUPONS)
    coupon_discount = COUPON_DISCOUNT.get(coupon, 0)

    # Effective discount (capped at 40%)
    effective_discount = min(base_discount + coupon_discount, 40)
    unit_price_after_discount = p['price'] * (1 - effective_discount / 100)
    total_price = round(unit_price_after_discount * quantity)

    # Shipping
    shipping_method = random.choices(SHIPPING_METHODS, weights=[40, 35, 10, 15])[0]
    shipping_fee = SHIPPING_FEES[shipping_method]
    if coupon == 'FREESHIP':
        shipping_fee = 0
    if total_price > 10e6:
        shipping_fee = 0  # Free ship for orders > 10M

    delivery_days_range = SHIPPING_DAYS[shipping_method]
    delivery_days = random.randint(delivery_days_range[0], delivery_days_range[1])

    # Order date with seasonal bias
    for _ in range(20):
        rand_days = random.randint(0, date_range_days)
        d = start_date + timedelta(days=rand_days)
        if random.random() < date_weight(d) / 2.0:
            break

    # Time of day (hour)
    if age < 30:
        hour = random.choices(range(24), weights=[1,1,1,0,0,0,1,2,3,4,5,6,7,8,8,7,6,5,6,8,9,8,5,3])[0]
    else:
        hour = random.choices(range(24), weights=[1,0,0,0,0,0,1,3,5,7,8,7,6,5,5,4,4,3,4,6,7,6,4,2])[0]
    minute = random.randint(0, 59)
    order_datetime = d.replace(hour=hour, minute=minute)

    # Status
    status = random.choice(STATUSES)

    # Rating: correlated with status and discount
    if status in ['Đã hủy', 'Đã hoàn trả', 'Đang xử lý hoàn trả']:
        rating = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
    elif status == 'Đã giao':
        rating = random.choices([1, 2, 3, 4, 5], weights=[2, 3, 8, 35, 52])[0]
    else:
        rating = random.choices([3, 4, 5], weights=[15, 45, 40])[0]

    review = random.choice(REVIEW_TEMPLATES[rating])

    # Payment & Device
    payment = get_payment(age, total_price)
    device = get_device(age, occ)

    # Customer type
    user_order_count[uid] += 1
    order_num = user_order_count[uid]
    if order_num == 1:
        customer_type = 'Khách mới'
    elif order_num <= 5:
        customer_type = 'Khách quay lại'
    else:
        customer_type = 'Khách VIP'

    # Is returned
    is_returned = status in ['Đã hoàn trả', 'Đang xử lý hoàn trả']
    return_reason = None
    if is_returned:
        return_reason = random.choice([
            'Sản phẩm lỗi', 'Không đúng mô tả', 'Đổi ý', 
            'Giao sai sản phẩm', 'Sản phẩm bị hư hỏng trong vận chuyển'
        ])

    orders.append({
        'order_id': f"SYN{order_counter:06d}",
        'user_id': uid,
        'name_user': user['name_user'],
        'age': age,
        'gender': user['gender'],
        'occupation': occ,
        'city': user['city'],
        'region': user['region'],
        'product_id': product_id,
        'name_product': p['name'],
        'category': p['category'],
        'brand': p['brand'],
        'price': p['price'],
        'rating_product': p['rating'],
        'discount': effective_discount,
        'coupon_code': coupon if coupon else '',
        'quantity': quantity,
        'total_price': total_price,
        'shipping_fee': shipping_fee,
        'total_with_shipping': total_price + shipping_fee,
        'total_price_million': round(total_price / 1e6, 3),
        'payment_method': payment,
        'device_type': device,
        'shipping_method': shipping_method,
        'delivery_days': delivery_days,
        'date': order_datetime.strftime('%Y-%m-%d'),
        'order_time': order_datetime.strftime('%H:%M'),
        'month': order_datetime.strftime('%Y-%m'),
        'day_of_week': order_datetime.strftime('%A'),
        'status': status,
        'customer_type': customer_type,
        'rating_order': rating,
        'review': review,
        'is_returned': is_returned,
        'return_reason': return_reason if return_reason else '',
    })
    order_counter += 1

df_orders_syn = pd.DataFrame(orders)

# ─── Save ─────────────────────────────────────────────────────────────────────
os.makedirs('d:/ok/data/csv', exist_ok=True)
csv_path = 'd:/ok/data/csv/synthetic_200k.csv'
df_orders_syn.to_csv(csv_path, index=False, encoding='utf-8-sig')

# ─── Stats ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"✅ Đã tạo {len(df_orders_syn):,} đơn hàng doanh nghiệp")
print(f"{'='*70}")
print(f"   Người dùng unique    : {df_orders_syn['user_id'].nunique():,}")
print(f"   Sản phẩm unique      : {df_orders_syn['product_id'].nunique()}")
print(f"   Danh mục             : {df_orders_syn['category'].nunique()}")
print(f"   Thành phố            : {df_orders_syn['city'].nunique()}")
print(f"   Doanh thu (tổng)     : {df_orders_syn['total_price'].sum()/1e9:.1f} tỷ VND")
print(f"   Doanh thu (+ ship)   : {df_orders_syn['total_with_shipping'].sum()/1e9:.1f} tỷ VND")
print(f"   Rating TB            : {df_orders_syn['rating_order'].mean():.2f}")
print(f"   Tỷ lệ hoàn trả      : {df_orders_syn['is_returned'].mean()*100:.1f}%")
print(f"   Thời gian            : {df_orders_syn['date'].min()} → {df_orders_syn['date'].max()}")
print(f"\n📊 Columns ({len(df_orders_syn.columns)}):")
for c in df_orders_syn.columns:
    print(f"   • {c}")

print(f"\n📄 Đã lưu: {csv_path}")
print(f"   File size: {os.path.getsize(csv_path)/1e6:.1f} MB")

# --- Top products ---
print(f"\n📦 TOP 10 sản phẩm bán chạy:")
top10 = df_orders_syn.groupby(['product_id','name_product'])['order_id'].count().sort_values(ascending=False).head(10)
for (pid, pname), cnt in top10.items():
    print(f"   ID {pid:2d}: {pname[:40]:40s} — {cnt:,} đơn")

# --- Payment stats ---
print(f"\n💳 Thanh toán:")
for pm, cnt in df_orders_syn['payment_method'].value_counts().items():
    print(f"   {pm:25s} — {cnt:,} ({cnt/len(df_orders_syn)*100:.1f}%)")

# --- Device stats ---
print(f"\n📱 Thiết bị:")
for dev, cnt in df_orders_syn['device_type'].value_counts().items():
    print(f"   {dev:10s} — {cnt:,} ({cnt/len(df_orders_syn)*100:.1f}%)")

# --- Status stats ---
print(f"\n📋 Trạng thái:")
for st, cnt in df_orders_syn['status'].value_counts().items():
    print(f"   {st:25s} — {cnt:,} ({cnt/len(df_orders_syn)*100:.1f}%)")

# --- Customer type ---
print(f"\n👥 Loại khách hàng:")
for ct, cnt in df_orders_syn['customer_type'].value_counts().items():
    print(f"   {ct:15s} — {cnt:,} ({cnt/len(df_orders_syn)*100:.1f}%)")
