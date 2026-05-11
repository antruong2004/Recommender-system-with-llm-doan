"""
╔══════════════════════════════════════════════════════════════════╗
║     TECHSTORE AI — MEGA DATA GENERATOR                          ║
║     50K Users | 400K Orders | 300K Reviews | 200K Behavior Logs ║
╚══════════════════════════════════════════════════════════════════╝
Generates massive synthetic dataset for AI training.
"""
import json, random, os, math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

DATA_DIR = 'd:/ok/data'

# ─── Load products ────────────────────────────────────────────────────────────
with open(f'{DATA_DIR}/products.json', encoding='utf-8') as f:
    products_raw = json.load(f)
product_ids = [p['id'] for p in products_raw]
product_map = {p['id']: p for p in products_raw}
print(f"✅ Loaded {len(products_raw)} products (IDs: {min(product_ids)}-{max(product_ids)})")

# Build category index
cat_products = {}
for p in products_raw:
    cat_products.setdefault(p['category'], [])
    cat_products[p['category']].append(p['id'])

# ─── Build 50,000 synthetic users ─────────────────────────────────────────────
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
    ("Quản lý dự án", "Nam", (28, 45)),
    ("UX/UI Designer", "Nữ", (23, 35)),
    ("QA/Tester", "Nam", (23, 35)),
    ("Kỹ sư AI/ML", "Nam", (24, 38)),
    ("Luật sư", "Nam", (28, 50)),
    ("Dược sĩ", "Nữ", (25, 45)),
    ("Chuyên viên tài chính", "Nam", (25, 42)),
    ("Chuyên viên SEO/Digital Marketing", "Nữ", (22, 35)),
    ("Video Editor", "Nam", (22, 38)),
    ("Thợ điện", "Nam", (22, 45)),
    ("Nhân viên logistics", "Nam", (22, 38)),
    ("Chủ shop online", "Nữ", (25, 45)),
    ("Giảng viên đại học", "Nam", (30, 55)),
    ("Thông dịch viên", "Nữ", (24, 40)),
    ("Kiểm toán viên", "Nam", (25, 42)),
    ("Nhân viên IT Support", "Nam", (22, 35)),
    ("Họa sĩ 3D", "Nam", (22, 38)),
    ("Motion Designer", "Nữ", (22, 35)),
    ("Phóng viên", "Nữ", (24, 38)),
    ("Phi công", "Nam", (28, 50)),
]

MALE_SURNAMES = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Vũ','Đặng','Bùi','Lý','Đỗ','Hồ','Trương','Ngô','Đinh','Lưu','Hà','Đào','Dương','Phan','Tô']
MALE_MIDNAMES = ['Văn','Minh','Đức','Trọng','Công','Hữu','Duy','Tiến','Quốc','Gia','Thanh','Tuấn','Anh','Hùng','Khoa','Phú']
MALE_NAMES = ['An','Hùng','Dũng','Cường','Phát','Giang','Khoa','Khánh','Luận','Minh','Nghĩa','Phúc','Quân','Sơn','Tân','Uy','Việt','Nhật','Long','Lâm','Bảo','Đạt','Hưng','Thành','Trung','Kiên','Hoàng','Nam','Tùng','Hải']
FEMALE_SURNAMES = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Vũ','Đặng','Bùi','Lý','Đỗ','Hồ','Trương','Ngô','Đinh','Phan','Lưu']
FEMALE_MIDNAMES = ['Thị','Ngọc','Lan','Thu','Mai','Thanh','Hồng','Bảo','Diễm','Quỳnh','Phương','Thùy','Kim']
FEMALE_NAMES = ['An','Bình','Chi','Dung','Em','Giang','Hoa','Lan','Linh','Ly','My','Ngân','Như','Oanh','Phương','Quỳnh','Tâm','Thanh','Thảo','Vy','Yến','Hạnh','Trâm','Nhi','Trang','Hằng','Châu','Diệu','Uyên','Khánh']

def gen_name(gender):
    if gender == 'Nam':
        return f"{random.choice(MALE_SURNAMES)} {random.choice(MALE_MIDNAMES)} {random.choice(MALE_NAMES)}"
    else:
        return f"{random.choice(FEMALE_SURNAMES)} {random.choice(FEMALE_MIDNAMES)} {random.choice(FEMALE_NAMES)}"

CITIES = [
    ("TP. Hồ Chí Minh", "Miền Nam", 25),
    ("Hà Nội", "Miền Bắc", 22),
    ("Đà Nẵng", "Miền Trung", 7),
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
    ("Bến Tre", "Miền Nam", 1),
    ("Thủ Đức", "Miền Nam", 1),
    ("Bình Dương", "Miền Nam", 1),
    ("Hạ Long", "Miền Bắc", 1),
    ("Ninh Bình", "Miền Bắc", 1),
    ("Lào Cai", "Miền Bắc", 1),
    ("Kon Tum", "Miền Trung", 1),
    ("Mỹ Tho", "Miền Nam", 1),
    ("Tây Ninh", "Miền Nam", 1),
]
CITY_NAMES = [c[0] for c in CITIES]
CITY_REGIONS = {c[0]: c[1] for c in CITIES}
CITY_WEIGHTS = [c[2] for c in CITIES]

# ─── Generate 50K users ──────────────────────────────────────────────────────
N_USERS = 50_000
print(f"\n👥 Generating {N_USERS:,} users ...")
users = []
occ_cycle = OCCUPATIONS * (N_USERS // len(OCCUPATIONS) + 1)
random.shuffle(occ_cycle)
for i in range(N_USERS):
    uid = f"SU{i+1:06d}"
    occ, gender, age_range = occ_cycle[i]
    age = random.randint(age_range[0], age_range[1])
    name = gen_name(gender)
    city = random.choices(CITY_NAMES, weights=CITY_WEIGHTS)[0]
    region = CITY_REGIONS[city]
    reg_date = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 730))
    users.append({
        'user_id': uid, 'name_user': name, 'age': age, 'gender': gender,
        'occupation': occ, 'city': city, 'region': region,
        'registration_date': reg_date.strftime('%Y-%m-%d'),
    })

df_users = pd.DataFrame(users)
print(f"✅ Generated {N_USERS:,} users across {df_users['city'].nunique()} cities")

# Save users
with open(f'{DATA_DIR}/users.json', 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=2)
df_users.to_csv(f'{DATA_DIR}/csv/users.csv', index=False, encoding='utf-8-sig')
print(f"   Saved users.json + users.csv")

# ─── Occupation preference map ───────────────────────────────────────────────
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
    "Quản lý dự án":         {'cats': ['Laptop','Điện thoại','Phụ kiện','Màn hình'], 'budget': (5e6,45e6)},
    "UX/UI Designer":        {'cats': ['Laptop','Màn hình','Máy tính bảng','Phụ kiện'], 'budget': (5e6,50e6)},
    "QA/Tester":             {'cats': ['Laptop','Màn hình','Phụ kiện'], 'budget': (4e6,35e6)},
    "Kỹ sư AI/ML":          {'cats': ['Laptop','Màn hình','Lưu trữ'], 'budget': (8e6,80e6)},
    "Luật sư":               {'cats': ['Điện thoại','Laptop','Đồng hồ thông minh'], 'budget': (8e6,50e6)},
    "Dược sĩ":              {'cats': ['Điện thoại','Đồng hồ thông minh','Máy tính bảng'], 'budget': (4e6,30e6)},
    "Chuyên viên tài chính": {'cats': ['Laptop','Điện thoại','Màn hình'], 'budget': (5e6,40e6)},
    "Chuyên viên SEO/Digital Marketing": {'cats': ['Laptop','Điện thoại','Phụ kiện'], 'budget': (4e6,30e6)},
    "Video Editor":          {'cats': ['Laptop','Màn hình','Lưu trữ','Phụ kiện'], 'budget': (8e6,60e6)},
    "Thợ điện":              {'cats': ['Điện thoại','Phụ kiện','Đồng hồ thông minh'], 'budget': (2e6,15e6)},
    "Nhân viên logistics":   {'cats': ['Điện thoại','Phụ kiện','Đồng hồ thông minh'], 'budget': (3e6,20e6)},
    "Chủ shop online":       {'cats': ['Điện thoại','Laptop','Phụ kiện','Máy ảnh'], 'budget': (3e6,30e6)},
    "Giảng viên đại học":    {'cats': ['Laptop','Màn hình','Phụ kiện','Lưu trữ'], 'budget': (5e6,45e6)},
    "Thông dịch viên":      {'cats': ['Laptop','Phụ kiện','Điện thoại'], 'budget': (3e6,25e6)},
    "Kiểm toán viên":       {'cats': ['Laptop','Màn hình','Phụ kiện'], 'budget': (5e6,35e6)},
    "Nhân viên IT Support":  {'cats': ['Laptop','Màn hình','Lưu trữ','Phụ kiện'], 'budget': (4e6,35e6)},
    "Họa sĩ 3D":            {'cats': ['Laptop','Màn hình','Máy tính bảng','Phụ kiện'], 'budget': (5e6,60e6)},
    "Motion Designer":       {'cats': ['Laptop','Màn hình','Phụ kiện','Lưu trữ'], 'budget': (5e6,50e6)},
    "Phóng viên":            {'cats': ['Máy ảnh','Laptop','Điện thoại','Phụ kiện'], 'budget': (5e6,40e6)},
    "Phi công":              {'cats': ['Đồng hồ thông minh','Điện thoại','Laptop'], 'budget': (10e6,60e6)},
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
    return pref_ids_filtered

# ─── Reviews templates ────────────────────────────────────────────────────────
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
        "Dùng một tuần rồi, rất ưng ý. Sẽ quay lại mua thêm.",
        "Sản phẩm xịn, đúng chính hãng. Đóng gói như quà tặng.",
    ],
    4: [
        "Sản phẩm tốt, giao hàng ổn. Hài lòng với đơn hàng này.",
        "Dùng được, đáng đồng tiền. Sẽ giới thiệu bạn bè.",
        "Tương đối ổn, nhưng pin hơi yếu hơn kỳ vọng một chút.",
        "Khá ưng ý, thiết kế đẹp. Chức năng như mô tả.",
        "Chất lượng tốt so với mức giá. Giao hàng đúng hạn.",
        "Sản phẩm như mô tả, đóng gói kỹ. Chỉ hơi lâu giao.",
        "Tạm hài lòng, sẽ cân nhắc mua thêm sản phẩm khác.",
        "Nhìn chung ổn, ngoại trừ một vài chi tiết nhỏ cần cải thiện.",
    ],
    3: [
        "Bình thường, không quá nổi bật so với giá tiền.",
        "Tạm ổn, nhưng giá hơi cao so với chất lượng nhận được.",
        "Dùng được nhưng không như kỳ vọng. Cần cải thiện thêm.",
        "Chấp nhận được, vẫn dùng tốt nhưng không ấn tượng.",
        "Trung bình, giao hàng hơi chậm. Sản phẩm tạm OK.",
        "Không tệ nhưng cũng không xuất sắc. Giá hợp lý thôi.",
    ],
    2: [
        "Hơi thất vọng so với kỳ vọng. Chất lượng chưa tương xứng giá.",
        "Giao hàng chậm, sản phẩm tạm. Cần cải thiện dịch vụ.",
        "Chất lượng không tốt bằng ảnh và mô tả. Hơi tiếc.",
        "Sản phẩm bị trầy nhẹ khi nhận. Đóng gói chưa tốt.",
        "Không đúng màu như hình. Hơi thất vọng một chút.",
    ],
    1: [
        "Sản phẩm kém chất lượng, rất không hài lòng.",
        "Không đúng mô tả, thất vọng hoàn toàn. Muốn đổi trả.",
        "Hàng lỗi, đã liên hệ đổi trả. Trải nghiệm rất tệ.",
        "Giao nhầm sản phẩm. Rất bực mình.",
    ]
}

# ─── Payment / Shipping / Device helpers ──────────────────────────────────────
PAYMENT_METHODS = ['COD', 'Thẻ tín dụng', 'Ví MoMo', 'Ví ZaloPay', 'Chuyển khoản ngân hàng', 'VNPay']

def get_payment(age, total_price):
    if age < 25:
        weights = [15, 10, 30, 25, 5, 15]
    elif age < 35:
        weights = [10, 20, 25, 15, 10, 20]
    elif age < 45:
        weights = [20, 25, 10, 8, 25, 12]
    else:
        weights = [30, 20, 5, 3, 30, 12]
    if total_price > 20e6:
        weights[1] += 15
        weights[4] += 10
        weights[0] = max(0, weights[0] - 10)
    return random.choices(PAYMENT_METHODS, weights=weights)[0]

DEVICE_TYPES = ['Mobile', 'Desktop', 'Tablet']

def get_device(age, occupation):
    if age < 30:
        weights = [65, 25, 10]
    elif age < 45:
        weights = [45, 40, 15]
    else:
        weights = [35, 45, 20]
    if any(kw in occupation for kw in ['Lập trình','Kỹ sư','DevOps','Data','AI/ML','IT Support','Video Editor','Họa sĩ','Motion']):
        weights = [30, 60, 10]
    if 'Sinh viên' in occupation:
        weights = [70, 20, 10]
    return random.choices(DEVICE_TYPES, weights=weights)[0]

COUPONS = [None]*60 + ['WELCOME10']*8 + ['FLASH20']*5 + ['TET2024']*4 + \
          ['SUMMER15']*5 + ['LOYAL30']*3 + ['TECH10']*5 + ['NEWUSER']*5 + \
          ['FREESHIP']*5
COUPON_DISCOUNT = {
    None: 0, 'WELCOME10': 10, 'FLASH20': 20, 'TET2024': 15,
    'SUMMER15': 15, 'LOYAL30': 30, 'TECH10': 10, 'NEWUSER': 10, 'FREESHIP': 0
}
SHIPPING_METHODS = ['Tiêu chuẩn', 'Nhanh', 'Hỏa tốc', 'Tiết kiệm']
SHIPPING_FEES = {'Tiêu chuẩn': 30000, 'Nhanh': 50000, 'Hỏa tốc': 80000, 'Tiết kiệm': 15000}
SHIPPING_DAYS = {'Tiêu chuẩn': (3, 5), 'Nhanh': (1, 3), 'Hỏa tốc': (1, 1), 'Tiết kiệm': (5, 8)}
STATUSES = ['Đã giao'] * 70 + ['Đang giao'] * 12 + ['Chờ xử lý'] * 8 + \
           ['Đã hủy'] * 5 + ['Đã hoàn trả'] * 3 + ['Đang xử lý hoàn trả'] * 2

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date - start_date).days

def date_weight(d):
    m = d.month
    if m in [1, 2]:   return 1.6
    if m in [11, 12]: return 1.9
    if m in [6, 7]:   return 1.3
    if m in [3]:      return 1.2
    if m in [10]:     return 1.1
    return 1.0

# ════════════════════════════════════════════════════════════════
# GENERATE 400,000 ORDERS
# ════════════════════════════════════════════════════════════════
N_ORDERS = 400_000
print(f"\n📦 Generating {N_ORDERS:,} orders ...")

# Ensure coverage: at least 10 orders per product (20K products × 10 = 200K guaranteed)
guaranteed_orders = []
for pid in product_ids:
    for _ in range(10):
        guaranteed_orders.append(pid)
random.shuffle(guaranteed_orders)
print(f"   Guaranteed pool: {len(guaranteed_orders):,} orders for product coverage")

user_order_count = {u['user_id']: 0 for u in users}
orders = []
order_counter = 1
guaranteed_idx = 0

for i in range(N_ORDERS):
    if i % 50000 == 0:
        print(f"   {i:,}/{N_ORDERS:,}...")

    user = users[random.randint(0, N_USERS - 1)]
    uid = user['user_id']
    occ = user['occupation']
    age = user['age']

    if guaranteed_idx < len(guaranteed_orders):
        product_id = guaranteed_orders[guaranteed_idx]
        guaranteed_idx += 1
    else:
        pref_pids = get_pref_products(occ)
        product_id = random.choice(pref_pids)

    p = product_map[product_id]
    quantity = random.choices([1, 2, 3], weights=[78, 17, 5])[0]
    base_discount = p.get('discount', 0)
    coupon = random.choice(COUPONS)
    coupon_discount = COUPON_DISCOUNT.get(coupon, 0)
    effective_discount = min(base_discount + coupon_discount, 40)
    unit_price_after_discount = p['price'] * (1 - effective_discount / 100)
    total_price = round(unit_price_after_discount * quantity)

    shipping_method = random.choices(SHIPPING_METHODS, weights=[40, 35, 10, 15])[0]
    shipping_fee = SHIPPING_FEES[shipping_method]
    if coupon == 'FREESHIP':
        shipping_fee = 0
    if total_price > 10e6:
        shipping_fee = 0

    delivery_days_range = SHIPPING_DAYS[shipping_method]
    delivery_days = random.randint(delivery_days_range[0], delivery_days_range[1])

    for _ in range(20):
        rand_days = random.randint(0, date_range_days)
        d = start_date + timedelta(days=rand_days)
        if random.random() < date_weight(d) / 2.0:
            break

    if age < 30:
        hour = random.choices(range(24), weights=[1,1,1,0,0,0,1,2,3,4,5,6,7,8,8,7,6,5,6,8,9,8,5,3])[0]
    else:
        hour = random.choices(range(24), weights=[1,0,0,0,0,0,1,3,5,7,8,7,6,5,5,4,4,3,4,6,7,6,4,2])[0]
    minute = random.randint(0, 59)
    order_datetime = d.replace(hour=hour, minute=minute)

    status = random.choice(STATUSES)

    if status in ['Đã hủy', 'Đã hoàn trả', 'Đang xử lý hoàn trả']:
        rating = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
    elif status == 'Đã giao':
        rating = random.choices([1, 2, 3, 4, 5], weights=[2, 3, 8, 35, 52])[0]
    else:
        rating = random.choices([3, 4, 5], weights=[15, 45, 40])[0]

    review = random.choice(REVIEW_TEMPLATES[rating])
    payment = get_payment(age, total_price)
    device = get_device(age, occ)

    user_order_count[uid] += 1
    order_num = user_order_count[uid]
    if order_num == 1:
        customer_type = 'Khách mới'
    elif order_num <= 5:
        customer_type = 'Khách quay lại'
    else:
        customer_type = 'Khách VIP'

    is_returned = status in ['Đã hoàn trả', 'Đang xử lý hoàn trả']
    return_reason = None
    if is_returned:
        return_reason = random.choice([
            'Sản phẩm lỗi', 'Không đúng mô tả', 'Đổi ý',
            'Giao sai sản phẩm', 'Sản phẩm bị hư hỏng trong vận chuyển'
        ])

    orders.append({
        'order_id': f"SYN{order_counter:07d}",
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

df_orders = pd.DataFrame(orders)
os.makedirs(f'{DATA_DIR}/csv', exist_ok=True)
csv_path = f'{DATA_DIR}/csv/synthetic_400k.csv'
df_orders.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"✅ Orders: {len(df_orders):,} | file: {csv_path} ({os.path.getsize(csv_path)/1e6:.1f} MB)")

# ════════════════════════════════════════════════════════════════
# GENERATE 300,000 REVIEWS
# ════════════════════════════════════════════════════════════════
N_REVIEWS = 300_000
print(f"\n⭐ Generating {N_REVIEWS:,} reviews ...")

REVIEW_TITLES = {
    5: ["Tuyệt vời!", "Xuất sắc!", "Rất hài lòng", "10/10", "Đáng mua!", "Chất lượng cao", "Recommend!", "Perfect!", "Tốt nhất!"],
    4: ["Tốt", "Hài lòng", "Được lắm", "OK", "Ổn áp", "Khá tốt", "Đáng tiền", "4 sao"],
    3: ["Bình thường", "Tạm được", "Trung bình", "Chấp nhận được", "Không ấn tượng", "3 sao"],
    2: ["Thất vọng", "Chưa ổn", "Cần cải thiện", "Không như kỳ vọng", "Hơi tệ"],
    1: ["Rất tệ", "Không đồng ý", "Thất vọng hoàn toàn", "Hàng lỗi", "Tệ nhất"],
}

REVIEW_PROS = [
    "Thiết kế đẹp", "Hiệu năng tốt", "Pin lâu", "Camera đẹp", "Màn hình sắc nét",
    "Giao hàng nhanh", "Đóng gói tốt", "Giá hợp lý", "Nhẹ, dễ mang", "Âm thanh hay",
    "Bàn phím gõ sướng", "Chống nước tốt", "Sạc nhanh", "Kết nối ổn định", "Dễ sử dụng",
    "Build quality tốt", "Tốc độ nhanh", "Dung lượng lớn", "Chống sốc tốt", "WiFi mạnh",
]
REVIEW_CONS = [
    "Pin hơi yếu", "Hơi nặng", "Giá cao", "Chưa có tiếng Việt", "Fan hơi ồn",
    "Nóng khi sử dụng lâu", "Phụ kiện đi kèm ít", "Bảo hành phức tạp", "Cáp sạc ngắn",
    "Ít màu sắc lựa chọn", "Không có jack 3.5mm", "Giao hàng chậm", "Chưa hỗ trợ 5G",
    "Bộ nhớ không mở rộng được", "Camera đêm chưa tốt", "Loa ngoài nhỏ", "Touch ID chậm",
]

reviews = []
review_counter = 1
# Distribute reviews across products and users
for i in range(N_REVIEWS):
    if i % 50000 == 0:
        print(f"   {i:,}/{N_REVIEWS:,}...")

    user = users[random.randint(0, N_USERS - 1)]
    product_id = random.choice(product_ids)
    p = product_map[product_id]

    rating = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 12, 35, 45])[0]

    title = random.choice(REVIEW_TITLES[rating])
    content = random.choice(REVIEW_TEMPLATES[rating])

    # Add pros/cons for detailed reviews
    if random.random() < 0.4:
        n_pros = random.randint(1, 3)
        n_cons = random.randint(0, 2) if rating >= 3 else random.randint(1, 3)
        pros = random.sample(REVIEW_PROS, n_pros)
        cons = random.sample(REVIEW_CONS, n_cons)
        if pros:
            content += " Ưu điểm: " + ", ".join(pros) + "."
        if cons:
            content += " Nhược điểm: " + ", ".join(cons) + "."

    # Review date: some time after purchase
    review_date = start_date + timedelta(days=random.randint(0, date_range_days))
    helpful_votes = 0
    if rating in [5, 1]:  # Extreme ratings get more votes
        helpful_votes = random.choices([0,1,2,3,5,10,20,50], weights=[40,20,15,10,8,4,2,1])[0]
    else:
        helpful_votes = random.choices([0,1,2,3,5], weights=[60,20,10,7,3])[0]

    is_verified = random.random() < 0.75  # 75% verified purchases

    reviews.append({
        'review_id': f"REV{review_counter:07d}",
        'user_id': user['user_id'],
        'product_id': product_id,
        'product_name': p['name'],
        'category': p['category'],
        'brand': p['brand'],
        'rating': rating,
        'title': title,
        'content': content,
        'pros': ", ".join(pros) if random.random() < 0.4 and 'pros' in dir() else "",
        'cons': ", ".join(cons) if random.random() < 0.4 and 'cons' in dir() else "",
        'helpful_votes': helpful_votes,
        'is_verified_purchase': is_verified,
        'review_date': review_date.strftime('%Y-%m-%d'),
        'review_time': f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
    })
    review_counter += 1

df_reviews = pd.DataFrame(reviews)
reviews_csv = f'{DATA_DIR}/csv/reviews_300k.csv'
df_reviews.to_csv(reviews_csv, index=False, encoding='utf-8-sig')
print(f"✅ Reviews: {len(df_reviews):,} | file: {reviews_csv} ({os.path.getsize(reviews_csv)/1e6:.1f} MB)")

# Also save as JSON
reviews_json_path = f'{DATA_DIR}/reviews.json'
# Save only first 10K to JSON (full data in CSV)
with open(reviews_json_path, 'w', encoding='utf-8') as f:
    json.dump(reviews[:10000], f, ensure_ascii=False, indent=2)
print(f"   JSON preview: {reviews_json_path} (first 10K)")

# ════════════════════════════════════════════════════════════════
# GENERATE 200,000 BEHAVIOR LOGS
# ════════════════════════════════════════════════════════════════
N_BEHAVIORS = 200_000
print(f"\n🔍 Generating {N_BEHAVIORS:,} behavior logs ...")

ACTION_TYPES = ['view', 'click', 'search', 'add_to_cart', 'wishlist', 'compare', 'share']
ACTION_WEIGHTS = [35, 25, 15, 12, 5, 5, 3]  # view is most common

SEARCH_QUERIES = [
    "iPhone 16", "Samsung Galaxy", "laptop gaming", "tai nghe bluetooth",
    "SSD 1TB", "MacBook Pro", "bàn phím cơ", "chuột không dây",
    "màn hình 4K", "đồng hồ thông minh", "camera mirrorless", "sạc nhanh",
    "iPad", "airpods", "Galaxy Watch", "RTX 4060", "NVMe", "gaming mouse",
    "loa bluetooth JBL", "ốp lưng iPhone", "webcam 4K", "router WiFi 6",
    "đồng hồ Garmin", "máy ảnh Sony", "GoPro", "DJI drone",
    "pin dự phòng", "USB hub", "bàn phím Keychron", "chuột Logitech",
    "laptop mỏng nhẹ", "điện thoại giá rẻ", "tablet học sinh", "màn hình cong",
    "ổ cứng di động", "thẻ nhớ 256GB", "Apple Watch", "Samsung Tab",
    "mic thu âm", "stream deck", "laptop Dell", "laptop ASUS"
]

REFERRERS = ['direct', 'google', 'facebook', 'zalo', 'tiktok', 'youtube', 'email', 'banner_ad', 'affiliate']
REFERRER_WEIGHTS = [25, 30, 15, 8, 8, 5, 4, 3, 2]

DEVICES_BEHAVIOR = ['Mobile', 'Desktop', 'Tablet']
BROWSERS = ['Chrome', 'Safari', 'Firefox', 'Edge', 'Samsung Internet', 'Cốc Cốc', 'Opera']
BROWSER_WEIGHTS = [45, 20, 8, 10, 8, 7, 2]

behaviors = []
behavior_counter = 1

# Create user sessions: each user has 1-10 sessions
user_sessions = {}
session_counter = 1

for i in range(N_BEHAVIORS):
    if i % 50000 == 0:
        print(f"   {i:,}/{N_BEHAVIORS:,}...")

    user = users[random.randint(0, N_USERS - 1)]
    uid = user['user_id']

    # Session management
    if uid not in user_sessions or random.random() < 0.15:  # 15% chance new session
        user_sessions[uid] = f"SES{session_counter:08d}"
        session_counter += 1
    session_id = user_sessions[uid]

    action_type = random.choices(ACTION_TYPES, weights=ACTION_WEIGHTS)[0]
    product_id = random.choice(product_ids) if action_type != 'search' else None
    p = product_map[product_id] if product_id else None

    # Timestamp
    log_date = start_date + timedelta(days=random.randint(0, date_range_days))
    hour = random.choices(range(24), weights=[1,1,0,0,0,0,1,3,5,7,8,7,6,5,5,4,4,3,5,7,8,7,4,2])[0]
    log_datetime = log_date.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))

    # Duration on page (seconds)
    if action_type == 'view':
        duration = random.choices([5,10,20,30,60,120,300], weights=[10,20,25,20,15,7,3])[0]
    elif action_type == 'click':
        duration = random.choices([1,3,5,10,20], weights=[15,30,30,20,5])[0]
    elif action_type == 'search':
        duration = random.choices([2,5,10,20], weights=[20,35,30,15])[0]
    else:
        duration = random.choices([1,2,5,10], weights=[30,30,25,15])[0]

    search_query = random.choice(SEARCH_QUERIES) if action_type == 'search' else ""
    referrer = random.choices(REFERRERS, weights=REFERRER_WEIGHTS)[0]
    device = random.choices(DEVICES_BEHAVIOR, weights=[55, 35, 10])[0]
    browser = random.choices(BROWSERS, weights=BROWSER_WEIGHTS)[0]

    behaviors.append({
        'log_id': f"LOG{behavior_counter:08d}",
        'user_id': uid,
        'session_id': session_id,
        'action_type': action_type,
        'product_id': product_id if product_id else '',
        'product_name': p['name'] if p else '',
        'category': p['category'] if p else '',
        'search_query': search_query,
        'timestamp': log_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'date': log_datetime.strftime('%Y-%m-%d'),
        'hour': hour,
        'duration_seconds': duration,
        'device_type': device,
        'browser': browser,
        'referrer': referrer,
        'page_url': f"/product/{product_id}" if product_id else "/search",
    })
    behavior_counter += 1

df_behaviors = pd.DataFrame(behaviors)
behaviors_csv = f'{DATA_DIR}/csv/behavior_logs_200k.csv'
df_behaviors.to_csv(behaviors_csv, index=False, encoding='utf-8-sig')
print(f"✅ Behavior logs: {len(df_behaviors):,} | file: {behaviors_csv} ({os.path.getsize(behaviors_csv)/1e6:.1f} MB)")

# Save as JSON (first 10K)
behaviors_json_path = f'{DATA_DIR}/behavior_logs.json'
with open(behaviors_json_path, 'w', encoding='utf-8') as f:
    json.dump(behaviors[:10000], f, ensure_ascii=False, indent=2)
print(f"   JSON preview: {behaviors_json_path} (first 10K)")

# ════════════════════════════════════════════════════════════════
# SUMMARY STATISTICS
# ════════════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print(f"{'='*70}")
print(f"  📊 MEGA DATA GENERATION — HOÀN THÀNH")
print(f"{'='*70}")
print(f"  👥 Users           : {len(users):>10,}")
print(f"  📦 Orders          : {len(df_orders):>10,}")
print(f"  ⭐ Reviews         : {len(df_reviews):>10,}")
print(f"  🔍 Behavior Logs   : {len(df_behaviors):>10,}")
print(f"  🏪 Products        : {len(products_raw):>10,}")
print(f"{'='*70}")
print(f"  💰 Doanh thu tổng  : {df_orders['total_price'].sum()/1e9:.1f} tỷ VND")
print(f"  ⭐ Rating TB orders: {df_orders['rating_order'].mean():.2f}")
print(f"  ⭐ Rating TB reviews: {df_reviews['rating'].mean():.2f}")
print(f"  📱 Thành phố       : {df_orders['city'].nunique()}")
print(f"  📁 Categories      : {df_orders['category'].nunique()}")
print(f"  📅 Date range      : {df_orders['date'].min()} → {df_orders['date'].max()}")
print(f"{'='*70}")

# File sizes
total_size = 0
for fpath in [csv_path, reviews_csv, behaviors_csv, f'{DATA_DIR}/csv/users.csv']:
    if os.path.exists(fpath):
        sz = os.path.getsize(fpath) / 1e6
        total_size += sz
        print(f"  📄 {os.path.basename(fpath):30s} {sz:>8.1f} MB")
print(f"  {'─'*40}")
print(f"  📄 {'Total CSV':30s} {total_size:>8.1f} MB")
print(f"{'='*70}")
