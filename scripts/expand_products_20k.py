"""
Expand products.json from 1,000 to 20,000 products.
Generates massive catalog of Vietnamese e-commerce tech products
by creating variants (storage, color, bundle, year) from base models.
"""
import json, random, copy, os, math

random.seed(2025)

DATA_DIR = 'd:/ok/data'

with open(f'{DATA_DIR}/products.json', encoding='utf-8') as f:
    existing = json.load(f)

print(f"Existing products: {len(existing)}")
max_id = max(p['id'] for p in existing)

# ── Target distribution for 20,000 products ──────────────────
TARGET_COUNT = {
    "Điện thoại": 3500,
    "Laptop": 3500,
    "Máy tính bảng": 1500,
    "Màn hình": 2000,
    "Đồng hồ thông minh": 1800,
    "Máy ảnh": 2000,
    "Lưu trữ": 2200,
    "Phụ kiện": 3500,
}

# ── Massive brand/model pools per category for generation ──────

PHONE_EXTRA_BRANDS = [
    "Motorola", "Honor", "Tecno", "Nokia", "Sony", "ASUS", "Huawei",
    "Nubia", "ZTE", "Infinix", "itel", "Alcatel", "TCL", "Meizu",
    "Poco", "Black Shark", "iQOO", "Lenovo", "HTC", "LG"
]
PHONE_SERIES = [
    "Pro Max", "Pro", "Plus", "Ultra", "Lite", "Neo", "FE", "SE",
    "5G", "Note", "Edge", "Flip", "Fold", "Mini", "Youth", "Turbo",
    "Speed", "Play", "Power", "Racing"
]
PHONE_CHIPS = [
    "Snapdragon 8 Elite", "Snapdragon 8 Gen 3", "Snapdragon 8s Gen 3",
    "Snapdragon 7 Gen 3", "Snapdragon 7s Gen 2", "Snapdragon 6 Gen 1",
    "Snapdragon 695", "Snapdragon 685", "Snapdragon 680",
    "Dimensity 9400", "Dimensity 9300", "Dimensity 9200",
    "Dimensity 8300", "Dimensity 7300", "Dimensity 6020",
    "Exynos 2400", "Exynos 1480", "Exynos 1380",
    "A18 Pro", "A18", "A17 Pro", "A16 Bionic", "A15 Bionic",
    "Helio G99", "Helio G85", "Unisoc T616", "Unisoc T612",
    "Tensor G4", "Tensor G3", "Kirin 9010", "Kirin 9000S"
]
PHONE_SCREENS = [
    "6.1 inch OLED", "6.3 inch AMOLED", "6.5 inch Super AMOLED",
    "6.6 inch LTPO AMOLED", "6.7 inch Dynamic AMOLED 2X",
    "6.78 inch AMOLED", "6.82 inch LTPO AMOLED",
    "6.9 inch Super Retina XDR OLED", "6.4 inch IPS LCD",
    "6.56 inch LCD", "6.67 inch AMOLED 120Hz", "6.73 inch LTPO AMOLED",
    "7.6 inch + 6.3 inch Foldable AMOLED", "6.7 inch + 3.4 inch Flip AMOLED"
]
PHONE_CAMERAS = [
    "200MP + 50MP + 12MP", "108MP + 8MP + 2MP", "50MP + 50MP + 50MP",
    "50MP + 12MP + 10MP", "50MP + 12MP", "50MP + 8MP + 2MP",
    "48MP + 12MP + 12MP", "48MP + 12MP", "64MP + 8MP + 2MP",
    "32MP + 8MP", "12MP + 12MP", "50MP Leica × 3", "50MP ZEISS × 3",
    "50MP Hasselblad × 4", "16MP + 5MP"
]
PHONE_BATTERIES = ["3500 mAh","4000 mAh","4500 mAh","4685 mAh","5000 mAh","5500 mAh","6000 mAh","6100 mAh"]
PHONE_STORAGES = ["64GB","128GB","256GB","512GB","1TB"]
PHONE_RAMS = ["4GB","6GB","8GB","12GB","16GB"]

LAPTOP_EXTRA_BRANDS = [
    "Gigabyte", "Razer", "LG", "Samsung", "Huawei", "Microsoft",
    "Framework", "Fujitsu", "Panasonic", "Toshiba/Dynabook",
    "Xiaomi", "Honor", "Chuwi", "Vaio", "Alienware"
]
LAPTOP_CHIPS = [
    "Intel Core Ultra 9 285H", "Intel Core Ultra 7 155H", "Intel Core Ultra 5 125H",
    "Intel Core Ultra 7 155U", "Intel Core Ultra 5 125U",
    "Intel Core i9-14900HX", "Intel Core i7-14700H", "Intel Core i7-13650HX",
    "Intel Core i7-1360P", "Intel Core i7-1355U", "Intel Core i5-1335U",
    "Intel Core i5-13420H", "Intel Core i3-1315U",
    "AMD Ryzen 9 8945HS", "AMD Ryzen 9 7945HX", "AMD Ryzen 7 8845HS",
    "AMD Ryzen 7 7745HX", "AMD Ryzen 7 7735HS", "AMD Ryzen 7 7730U",
    "AMD Ryzen 5 7535U", "AMD Ryzen 5 7530U",
    "Apple M4 Max", "Apple M4 Pro", "Apple M4", "Apple M3 Pro", "Apple M3", "Apple M2"
]
LAPTOP_GPUS = [
    "NVIDIA RTX 5090", "NVIDIA RTX 5080", "NVIDIA RTX 5070",
    "NVIDIA RTX 4090", "NVIDIA RTX 4080", "NVIDIA RTX 4070",
    "NVIDIA RTX 4060", "NVIDIA RTX 4050", "NVIDIA RTX 3050",
    "Intel Arc Graphics", "Intel Arc 140V", "Intel Iris Xe",
    "Intel UHD", "AMD Radeon 780M", "AMD Radeon 680M", "AMD Radeon",
    "10-core GPU", "18-core GPU", "40-core GPU"
]
LAPTOP_SCREENS = [
    "13.3 inch FHD IPS", "13.6 inch Liquid Retina", "14 inch FHD IPS",
    "14 inch 2.8K OLED", "14 inch 3K OLED", "14.2 inch Liquid Retina XDR",
    "15.6 inch FHD IPS", "15.6 inch FHD 144Hz", "15.6 inch QHD 165Hz",
    "16 inch FHD+", "16 inch QHD+ 165Hz", "16 inch WQXGA 240Hz",
    "16 inch 4K OLED", "16.2 inch Liquid Retina XDR",
    "17.3 inch FHD 144Hz", "17.3 inch QHD 240Hz"
]

MONITOR_EXTRA_BRANDS = [
    "ViewSonic", "AOC", "Gigabyte", "MSI", "Philips", "BenQ",
    "Acer", "Corsair", "Alienware", "Xiaomi", "HKC", "Prism",
    "Titan Army", "KTC", "Innocn", "Eve Spectrum"
]
MONITOR_SIZES = ["24 inch","27 inch","28 inch","32 inch","34 inch","38 inch","42 inch","49 inch"]
MONITOR_PANELS = ["IPS","VA","OLED","IPS Black","Mini LED","Nano IPS","Fast IPS"]
MONITOR_RESOLUTIONS = ["1920x1080 FHD","2560x1440 QHD","3440x1440 UWQHD","3840x2160 4K","5120x1440 DQHD","5120x2880 5K","6144x3456 6K"]
MONITOR_REFRESH = ["60Hz","75Hz","100Hz","120Hz","144Hz","165Hz","180Hz","240Hz","360Hz"]

WATCH_EXTRA_BRANDS = [
    "Amazfit", "Huawei", "OPPO", "Fitbit", "Mobvoi", "Coros",
    "Suunto", "Polar", "Fossil", "Casio", "Realme", "OnePlus",
    "Nothing", "CMF", "Noise", "boAt"
]
WATCH_SCREENS = [
    "1.2 inch AMOLED", "1.3 inch AMOLED", "1.39 inch AMOLED",
    "1.43 inch AMOLED", "1.47 inch Super AMOLED", "1.6 inch AMOLED",
    "1.93 inch LTPO OLED", "1.96 inch LTPO OLED", "1.4 inch MIP",
    "1 inch LCD", "1.1 inch MIP"
]
WATCH_SENSORS = [
    "nhịp tim, SpO2", "nhịp tim, SpO2, GPS", "ECG, SpO2, nhiệt độ",
    "nhịp tim, SpO2, giấc ngủ", "BIA, ECG, SpO2, nhiệt độ",
    "nhịp tim, SpO2, la bàn, bản đồ, GPS", "nhịp tim, gia tốc",
    "nhịp tim, SpO2, stress, giấc ngủ"
]

CAMERA_EXTRA_BRANDS = [
    "Sony", "Canon", "Fujifilm", "Nikon", "GoPro", "DJI",
    "Panasonic", "OM System", "Leica", "Insta360", "Hasselblad",
    "Phase One", "Ricoh", "Sigma", "Blackmagic"
]
CAMERA_SENSORS = [
    "61MP Full-Frame CMOS", "45.7MP Full-Frame CMOS", "33MP Full-Frame CMOS",
    "24.2MP Full-Frame CMOS", "40.2MP APS-C X-Trans CMOS",
    "26.1MP APS-C CMOS", "20.1MP 1 inch CMOS", "48MP 1/1.3 inch CMOS",
    "27MP", "20MP MFT", "24MP Full-Frame", "50MP Medium Format",
    "102MP Medium Format", "47.3MP Full-Frame BSI CMOS"
]
CAMERA_VIDEOS = [
    "8K 30fps","8K 24fps","6K 60fps","6.2K 30fps","5.3K 60fps",
    "4K 120fps","4K 60fps","4K 30fps","1080p 240fps"
]

STORAGE_EXTRA_BRANDS = [
    "Crucial", "SK hynix", "Corsair", "Lexar", "ADATA",
    "Sabrent", "PNY", "Phison", "Patriot", "Plextor",
    "Transcend", "Teamgroup", "Netac", "Hikvision", "Addlink"
]
STORAGE_SPEEDS_READ = ["560 MB/s","2100 MB/s","3500 MB/s","5000 MB/s","7000 MB/s","7450 MB/s","10000 MB/s","12400 MB/s"]
STORAGE_SPEEDS_WRITE = ["530 MB/s","1700 MB/s","3000 MB/s","4500 MB/s","6300 MB/s","6900 MB/s","8500 MB/s","11800 MB/s"]

ACCESSORY_EXTRA_BRANDS = [
    "Logitech", "Razer", "Corsair", "SteelSeries", "HyperX",
    "Keychron", "Akko", "Royal Kludge", "Ducky", "Leopold",
    "Elgato", "Rode", "Blue", "Audio-Technica", "Sennheiser",
    "Jabra", "Beyerdynamic", "Anker", "Ugreen", "Baseus",
    "Belkin", "Nillkin", "Spigen", "UAG", "Ringke", "ESR",
    "TP-Link", "ASUS", "Netgear", "Ubiquiti", "Synology", "QNAP"
]
ACCESSORY_TYPES_LIST = [
    "Tai nghe", "Bàn phím", "Chuột", "Sạc & Cáp", "Loa",
    "Bao da / Ốp lưng", "Webcam", "Microphone", "Mouse Pad",
    "Laptop Stand", "USB Hub / Dock", "Dán cường lực",
    "Adapter", "Bút cảm ứng", "Tracker", "Router",
    "Mesh WiFi", "NAS", "KVM Switch", "Headphone Stand",
    "Cable Management", "Docking Station", "Cooling Pad",
    "Wrist Rest", "Monitor Arm", "Desk Light", "Stream Deck"
]

# ── Color pools ──────────────────────────────────────────────
COLOR_POOLS = [
    ["Đen", "Trắng", "Bạc"],
    ["Đen", "Xanh", "Tím"],
    ["Đen", "Trắng", "Xanh", "Hồng"],
    ["Titan Tự Nhiên", "Titan Xanh", "Titan Đen"],
    ["Xám", "Đen", "Bạc"],
    ["Đen", "Kem", "Xanh Dương"],
    ["Đen", "Xanh Lá", "Đỏ"],
    ["Trắng", "Xám", "Vàng Sao"],
    ["Đen Obsidian", "Trắng Porcelain", "Xanh Hazel"],
    ["Đen", "Trắng"],
]

TAG_POOLS = {
    "Điện thoại": ["5G","AMOLED","sạc nhanh","camera AI","pin trâu","flagship","gaming","FaceID","Dynamic Island","Galaxy AI","Leica","ZEISS","Hasselblad","mỏng nhẹ","chống nước","chụp ảnh đẹp","NFC","eSIM","hiệu năng cao","giá tốt"],
    "Laptop": ["mỏng nhẹ","OLED","gaming","RTX","Thunderbolt","USB-C","pin trâu","chip Apple Silicon","Retina","macOS","Windows","doanh nhân","creator","hiệu năng cao","bàn phím tốt","2-in-1","touchscreen","MIL-STD","AI PC","Copilot"],
    "Máy tính bảng": ["Apple Pencil","S Pen","M4","mỏng nhẹ","Retina","iPadOS","Android","giải trí","học tập","vẽ","pin trâu","5G","WiFi 6","USB-C","120Hz","keyboard compatible"],
    "Màn hình": ["gaming","4K","OLED","HDR","USB-C","Curved","Mini LED","chuyên nghiệp","240Hz","144Hz","FreeSync","G-Sync","eye-care","UltraWide","nano IPS","KVM"],
    "Đồng hồ thông minh": ["sức khỏe","thể thao","GPS","ECG","SpO2","pin trâu","AMOLED","chống nước","BIA","solar","outdoor","Wear OS","watchOS","bản đồ","stress","giấc ngủ"],
    "Máy ảnh": ["mirrorless","full-frame","4K","8K","AI AF","chuyên nghiệp","vlog","retro","Instax","action cam","drone","gimbal","cinema","medium format","film simulation"],
    "Lưu trữ": ["SSD","NVMe","PCIe 5.0","PCIe 4.0","HDD","portable","gaming","tốc độ cao","bền bỉ","RAID","NAS","microSD","USB-C","Thunderbolt","encryption"],
    "Phụ kiện": ["wireless","bluetooth","ANC","mechanical","RGB","gaming","ergonomic","chống ồn","sạc nhanh","GaN","MagSafe","USB-C","hot-swap","chất lượng cao","chính hãng"],
}

# ── Helper functions ──────────────────────────────────────────

def gen_description(name, category, brand, specs):
    if category == "Điện thoại":
        return f"{name} - điện thoại {brand} với {specs.get('chip','')}, camera {specs.get('camera','')}, màn hình {specs.get('screen','')}, pin {specs.get('battery','')}, hỗ trợ {specs.get('os','')}."
    elif category == "Laptop":
        return f"{name} - laptop {brand} trang bị {specs.get('chip','')}, RAM {specs.get('ram','')}, ổ cứng {specs.get('storage','')}, card {specs.get('gpu','')}, màn hình {specs.get('screen','')}."
    elif category == "Máy tính bảng":
        return f"{name} - máy tính bảng {brand} chip {specs.get('chip','')}, màn hình {specs.get('screen','')}, pin {specs.get('battery','')}, {specs.get('os','')}."
    elif category == "Màn hình":
        return f"{name} - màn hình {brand} {specs.get('panel','')}, độ phân giải {specs.get('resolution','')}, tần số {specs.get('refresh','')}, HDR: {specs.get('hdr','')}."
    elif category == "Đồng hồ thông minh":
        return f"{name} - đồng hồ thông minh {brand} màn hình {specs.get('screen','')}, pin {specs.get('battery','')}, chống nước {specs.get('water','')}, cảm biến {specs.get('sensors','')}."
    elif category == "Máy ảnh":
        return f"{name} - máy ảnh {brand} cảm biến {specs.get('sensor','')}, quay video {specs.get('video','')}, AF {specs.get('af','')}, ISO {specs.get('iso','')}."
    elif category == "Lưu trữ":
        return f"{name} - ổ lưu trữ {brand} dung lượng {specs.get('capacity','')}, tốc độ đọc {specs.get('read','')}, ghi {specs.get('write','')}, chuẩn {specs.get('interface','')}."
    elif category == "Phụ kiện":
        return f"{name} - phụ kiện {brand} chất lượng cao, thiết kế hiện đại, tương thích đa thiết bị."
    return f"{name} - sản phẩm công nghệ {brand} chất lượng cao."


def create_product(pid, name, category, brand, price, original_price, specs, colors, tags):
    discount = max(0, min(40, round((1 - price / original_price) * 100)))
    rating = round(random.uniform(3.5, 4.9), 1)
    reviews = random.randint(20, 3000)
    stock = random.randint(3, 300)
    desc = gen_description(name, category, brand, specs)
    return {
        "id": pid,
        "name": name,
        "category": category,
        "brand": brand,
        "price": price,
        "original_price": original_price,
        "discount": discount,
        "rating": rating,
        "reviews": reviews,
        "stock": stock,
        "description": desc,
        "specs": specs,
        "colors": colors,
        "tags": random.sample(tags, min(len(tags), random.randint(3, 6))),
    }


# ── Build new products ─────────────────────────────────────────
new_products = list(existing)
next_id = max_id + 1
existing_names = {p['name'] for p in existing}

def add_product(name, category, brand, price, orig_price, specs, colors=None, tags=None):
    global next_id
    if name in existing_names:
        return False
    existing_names.add(name)
    c = colors or random.choice(COLOR_POOLS)
    t = tags or TAG_POOLS.get(category, ["chất lượng cao"])
    p = create_product(next_id, name, category, brand, price, orig_price, specs, c, t)
    new_products.append(p)
    next_id += 1
    return True

def gen_price(base_min, base_max):
    return int(round(random.randint(base_min, base_max) / 10000) * 10000)


# ════════════════════════════════════════════════════════════
# GENERATE PHONES  (~3500 target)
# ════════════════════════════════════════════════════════════
print("\n📱 Generating phones...")

ALL_PHONE_BRANDS = [
    "Apple","Samsung","Xiaomi","OPPO","vivo","realme","Google","Nothing","OnePlus"
] + PHONE_EXTRA_BRANDS

for brand in ALL_PHONE_BRANDS:
    # Generate 50-150 models per brand
    n_models = random.randint(40, 130)
    for _ in range(n_models):
        series_num = random.randint(1, 30)
        series = random.choice(PHONE_SERIES)
        storage = random.choice(PHONE_STORAGES)
        name = f"{brand} {random.choice(['','Galaxy ','Redmi ','Note ','','','',''])}{series_num} {series} {storage}".replace("  "," ").strip()
        
        chip = random.choice(PHONE_CHIPS)
        ram = random.choice(PHONE_RAMS)
        screen = random.choice(PHONE_SCREENS)
        camera = random.choice(PHONE_CAMERAS)
        battery = random.choice(PHONE_BATTERIES)
        os_ver = random.choice(["Android 14","Android 15","iOS 18","iOS 17","HarmonyOS 4"])
        
        price = gen_price(2000000, 45000000)
        orig = int(price * random.uniform(1.05, 1.25))
        
        specs = {"screen": screen, "chip": chip, "ram": ram, "storage": storage,
                 "camera": camera, "battery": battery, "os": os_ver}
        add_product(name, "Điện thoại", brand, price, orig, specs)
        
        if len([p for p in new_products if p['category'] == 'Điện thoại']) >= TARGET_COUNT['Điện thoại']:
            break
    if len([p for p in new_products if p['category'] == 'Điện thoại']) >= TARGET_COUNT['Điện thoại']:
        break

phone_count = len([p for p in new_products if p['category'] == 'Điện thoại'])
print(f"  Phones: {phone_count}")

# ════════════════════════════════════════════════════════════
# GENERATE LAPTOPS  (~3500 target)
# ════════════════════════════════════════════════════════════
print("\n💻 Generating laptops...")

ALL_LAPTOP_BRANDS = [
    "Apple","Dell","Lenovo","ASUS","HP","Acer","MSI"
] + LAPTOP_EXTRA_BRANDS
LAPTOP_SERIES = [
    "Pro","Air","Ultra","Studio","Slim","Plus","","EVO","Workstation",
    "Creator","Gaming","Essentials","Business","Everyday"
]
LAPTOP_RAMS = ["8GB","16GB","24GB","32GB","64GB"]
LAPTOP_STORAGES = ["256GB SSD","512GB SSD","1TB SSD","2TB SSD"]
LAPTOP_BATTERIES = ["41Wh","50Wh","56Wh","65Wh","72Wh","80Wh","86Wh","99.9Wh"]

for brand in ALL_LAPTOP_BRANDS:
    n_models = random.randint(40, 150)
    for _ in range(n_models):
        series_name = random.choice(LAPTOP_SERIES)
        screen_size = random.choice(["13","14","15","16","17"])
        storage = random.choice(LAPTOP_STORAGES)
        year = random.choice(["2024","2025","Gen 12","Gen 11","Gen 6","Gen 5","Mark II",""])
        name = f"{brand} {series_name} {screen_size} {year} {storage}".replace("  "," ").strip()
        
        chip = random.choice(LAPTOP_CHIPS)
        ram = random.choice(LAPTOP_RAMS)
        gpu = random.choice(LAPTOP_GPUS)
        screen = random.choice(LAPTOP_SCREENS)
        battery = random.choice(LAPTOP_BATTERIES)
        os_ver = random.choice(["Windows 11","Windows 11 Pro","macOS Sequoia","macOS Sonoma"])
        
        price = gen_price(8000000, 90000000)
        orig = int(price * random.uniform(1.05, 1.2))
        
        specs = {"screen": screen, "chip": chip, "ram": ram, "storage": storage,
                 "gpu": gpu, "battery": battery, "os": os_ver}
        add_product(name, "Laptop", brand, price, orig, specs)
        
        if len([p for p in new_products if p['category'] == 'Laptop']) >= TARGET_COUNT['Laptop']:
            break
    if len([p for p in new_products if p['category'] == 'Laptop']) >= TARGET_COUNT['Laptop']:
        break

laptop_count = len([p for p in new_products if p['category'] == 'Laptop'])
print(f"  Laptops: {laptop_count}")

# ════════════════════════════════════════════════════════════
# GENERATE TABLETS  (~1500 target)
# ════════════════════════════════════════════════════════════
print("\n📱 Generating tablets...")

TABLET_BRANDS = [
    "Apple","Samsung","Xiaomi","Lenovo","Huawei","OPPO","vivo",
    "realme","Nokia","Microsoft","Amazon","TCL","Blackview","Teclast",
    "Doogee","Alldocube"
]
TABLET_SERIES = ["Pro","Air","SE","FE","Plus","Ultra","Mini","Pad","Tab","Go","Lite","Standard","Active","Kids"]
TABLET_CHIPS = [
    "Apple M4","Apple M2","Apple M1","A17 Pro","A15 Bionic","A14 Bionic",
    "Snapdragon 8 Gen 2","Snapdragon 870","Snapdragon 695","Snapdragon 680",
    "Dimensity 9300+","Dimensity 9200","Dimensity 8300","Dimensity 7050",
    "Exynos 1380","Helio G99","Helio G85","Unisoc T616"
]
TABLET_SCREENS = [
    "8.3 inch Liquid Retina","10.2 inch Retina","10.9 inch Liquid Retina",
    "11 inch Liquid Retina XDR OLED","11 inch LCD 120Hz","11 inch LCD 144Hz",
    "12.4 inch Dynamic AMOLED 2X","12.9 inch Liquid Retina XDR",
    "13 inch Liquid Retina XDR OLED","14.6 inch Dynamic AMOLED 2X",
    "10.1 inch LCD","10.6 inch LCD", "11.5 inch OLED"
]
TABLET_STORAGES = ["64GB","128GB","256GB","512GB","1TB"]

for brand in TABLET_BRANDS:
    n_models = random.randint(30, 100)
    for _ in range(n_models):
        series = random.choice(TABLET_SERIES)
        storage = random.choice(TABLET_STORAGES)
        connectivity = random.choice(["WiFi","WiFi + 5G","WiFi + LTE"])
        name = f"{brand} {series} {random.randint(1,15)} {storage} {connectivity}"
        
        chip = random.choice(TABLET_CHIPS)
        screen = random.choice(TABLET_SCREENS)
        battery = f"{random.randint(5000,12000)} mAh"
        os_ver = random.choice(["iPadOS 18","iPadOS 17","Android 14","Android 13","HarmonyOS 4"])
        
        price = gen_price(3000000, 45000000)
        orig = int(price * random.uniform(1.05, 1.25))
        
        specs = {"screen": screen, "chip": chip, "ram": random.choice(["4GB","6GB","8GB","12GB","16GB"]),
                 "storage": storage, "camera": random.choice(["8MP","12MP","13MP","50MP"]),
                 "battery": battery, "os": os_ver}
        add_product(name, "Máy tính bảng", brand, price, orig, specs)
        
        if len([p for p in new_products if p['category'] == 'Máy tính bảng']) >= TARGET_COUNT['Máy tính bảng']:
            break
    if len([p for p in new_products if p['category'] == 'Máy tính bảng']) >= TARGET_COUNT['Máy tính bảng']:
        break

tablet_count = len([p for p in new_products if p['category'] == 'Máy tính bảng'])
print(f"  Tablets: {tablet_count}")

# ════════════════════════════════════════════════════════════
# GENERATE MONITORS  (~2000 target)
# ════════════════════════════════════════════════════════════
print("\n🖥️ Generating monitors...")

ALL_MONITOR_BRANDS = [
    "LG","Samsung","Dell","ASUS","BenQ","HP","Acer"
] + MONITOR_EXTRA_BRANDS

for brand in ALL_MONITOR_BRANDS:
    n_models = random.randint(30, 120)
    for _ in range(n_models):
        size = random.choice(MONITOR_SIZES)
        panel = random.choice(MONITOR_PANELS)
        res = random.choice(MONITOR_RESOLUTIONS)
        refresh = random.choice(MONITOR_REFRESH)
        model_code = f"{''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ',k=2))}{random.randint(100,9999)}"
        name = f"{brand} {model_code} {size} {res.split()[-1]} {panel} {refresh}"
        
        price = gen_price(2000000, 50000000)
        orig = int(price * random.uniform(1.05, 1.2))
        
        hdr = random.choice(["No","HDR400","HDR600","HDR1000","HDR True Black 400","HDR10","HDR10+"])
        response = random.choice(["0.03ms","0.1ms","1ms","4ms","5ms"])
        ports = random.choice([
            "HDMI x2, DP 1.4",
            "HDMI 2.1 x2, DP 1.4 x2",
            "HDMI, DP, USB-C 90W",
            "HDMI x2, USB-C 65W",
            "HDMI 2.1, DP 1.4, USB-C, USB Hub",
            "Thunderbolt 4, HDMI, USB-C"
        ])
        
        specs = {"panel": f"{size} {panel}", "resolution": res, "refresh": refresh,
                 "response": response, "hdr": hdr, "ports": ports}
        add_product(name, "Màn hình", brand, price, orig, specs)
        
        if len([p for p in new_products if p['category'] == 'Màn hình']) >= TARGET_COUNT['Màn hình']:
            break
    if len([p for p in new_products if p['category'] == 'Màn hình']) >= TARGET_COUNT['Màn hình']:
        break

monitor_count = len([p for p in new_products if p['category'] == 'Màn hình'])
print(f"  Monitors: {monitor_count}")

# ════════════════════════════════════════════════════════════
# GENERATE SMARTWATCHES  (~1800 target)
# ════════════════════════════════════════════════════════════
print("\n⌚ Generating smartwatches...")

ALL_WATCH_BRANDS = [
    "Apple","Samsung","Garmin","Xiaomi"
] + WATCH_EXTRA_BRANDS
WATCH_SERIES = [
    "Ultra","Pro","SE","Classic","Active","Sport","Lite","FE",
    "GT","GTS","GTR","Band","Fit","Sense","Charge","Versa",
    "Instinct","Forerunner","Venu","Fenix","Pace","Vertix"
]

for brand in ALL_WATCH_BRANDS:
    n_models = random.randint(25, 100)
    for _ in range(n_models):
        series = random.choice(WATCH_SERIES)
        ver = random.randint(1, 10)
        size = random.choice(["40mm","42mm","44mm","45mm","46mm","47mm","49mm","51mm",""])
        name = f"{brand} {series} {ver} {size}".strip()
        
        screen = random.choice(WATCH_SCREENS)
        battery = random.choice(["5 ngày","7 ngày","14 ngày","18 giờ","21 ngày","30 giờ","48 ngày","Không giới hạn Solar"])
        water = random.choice(["30m","50m","100m"])
        sensors = random.choice(WATCH_SENSORS)
        os_ver = random.choice(["watchOS 11","watchOS 10","Wear OS 5","Wear OS 4","Garmin OS","Zepp OS","HarmonyOS","–"])
        
        price = gen_price(500000, 25000000)
        orig = int(price * random.uniform(1.05, 1.25))
        
        specs = {"screen": screen, "chip": "–", "battery": battery,
                 "water": water, "os": os_ver, "sensors": sensors}
        add_product(name, "Đồng hồ thông minh", brand, price, orig, specs)
        
        if len([p for p in new_products if p['category'] == 'Đồng hồ thông minh']) >= TARGET_COUNT['Đồng hồ thông minh']:
            break
    if len([p for p in new_products if p['category'] == 'Đồng hồ thông minh']) >= TARGET_COUNT['Đồng hồ thông minh']:
        break

watch_count = len([p for p in new_products if p['category'] == 'Đồng hồ thông minh'])
print(f"  Smartwatches: {watch_count}")

# ════════════════════════════════════════════════════════════
# GENERATE CAMERAS  (~2000 target)
# ════════════════════════════════════════════════════════════
print("\n📷 Generating cameras...")

CAMERA_SERIES = [
    "Alpha","EOS","X-T","X-S","X-H","Z","ZV","HERO","Osmo","Pocket",
    "Mini","Air","Mavic","Lumix","OM-","Q","M","SL","D","Ace","X4","ONE",
    "BMPCC","FX","Cinema","Mark","R","II","III"
]

for brand in CAMERA_EXTRA_BRANDS:
    n_models = random.randint(30, 150)
    for _ in range(n_models):
        series = random.choice(CAMERA_SERIES)
        ver = random.choice(["","II","III","IV","V","",str(random.randint(1,99))])
        suffix = random.choice(["Body","Kit 18-55mm","Kit 24-70mm","","Fly More Combo","Creator Edition"])
        name = f"{brand} {series} {ver} {suffix}".replace("  "," ").strip()
        
        sensor = random.choice(CAMERA_SENSORS)
        video = random.choice(CAMERA_VIDEOS)
        iso = random.choice(["50-204800","100-51200","64-51200","100-25600","100-12800","100-6400"])
        af = random.choice(["759 điểm AI AF","1053 điểm Dual Pixel","425 điểm","493 điểm 3D tracking","Phase Detect AF","DFD AF","–"])
        evf = random.choice(["3.69M dot OLED","2.36M dot OLED","5.76M dot OLED","–"])
        weight = f"{random.randint(150,900)}g"
        
        price = gen_price(2000000, 90000000)
        orig = int(price * random.uniform(1.05, 1.2))
        
        specs = {"sensor": sensor, "iso": iso, "video": video,
                 "af": af, "evf": evf, "weight": weight}
        add_product(name, "Máy ảnh", brand, price, orig, specs)
        
        if len([p for p in new_products if p['category'] == 'Máy ảnh']) >= TARGET_COUNT['Máy ảnh']:
            break
    if len([p for p in new_products if p['category'] == 'Máy ảnh']) >= TARGET_COUNT['Máy ảnh']:
        break

camera_count = len([p for p in new_products if p['category'] == 'Máy ảnh'])
print(f"  Cameras: {camera_count}")

# ════════════════════════════════════════════════════════════
# GENERATE STORAGE  (~2200 target)
# ════════════════════════════════════════════════════════════
print("\n💾 Generating storage...")

ALL_STORAGE_BRANDS = [
    "Samsung","Western Digital","Seagate","Kingston"
] + STORAGE_EXTRA_BRANDS
STORAGE_TYPES = ["NVMe M.2 2280","2.5 inch SATA","Portable USB 3.2","Portable HDD","microSD","CFexpress","M.2 2230"]
STORAGE_INTERFACES = ["PCIe 5.0 x4","PCIe 4.0 x4","SATA III","USB 3.2 Gen 2","USB 3.2 Gen 2x2","USB 3.0","UHS-I U3","UHS-II"]
STORAGE_CAPACITIES = ["128GB","256GB","500GB","512GB","1TB","2TB","4TB","8TB","16TB"]
STORAGE_SERIES = [
    "Pro","EVO","Plus","Extreme","Black","Blue","Red","Green","Platinum",
    "Renegade","Fury","FireCuda","BarraCuda","IronWolf","One Touch",
    "My Passport","T7","T9","Rocket","Legend","Elite","NV","Canvas",
    "Expansion","Basic","Ultra","Performance","Max","Prime"
]

for brand in ALL_STORAGE_BRANDS:
    n_models = random.randint(30, 150)
    for _ in range(n_models):
        series = random.choice(STORAGE_SERIES)
        capacity = random.choice(STORAGE_CAPACITIES)
        stype = random.choice(STORAGE_TYPES)
        interface = random.choice(STORAGE_INTERFACES)
        name = f"{brand} {series} {capacity} {stype.split()[0]}"
        
        read_speed = random.choice(STORAGE_SPEEDS_READ)
        write_speed = random.choice(STORAGE_SPEEDS_WRITE)
        endurance = random.choice(["300 TBW", "600 TBW", "1200 TBW", "2400 TBW", "–"])
        
        price = gen_price(200000, 15000000)
        orig = int(price * random.uniform(1.05, 1.2))
        
        specs = {"type": stype, "interface": interface, "read": read_speed,
                 "write": write_speed, "capacity": capacity, "endurance": endurance}
        add_product(name, "Lưu trữ", brand, price, orig, specs)
        
        if len([p for p in new_products if p['category'] == 'Lưu trữ']) >= TARGET_COUNT['Lưu trữ']:
            break
    if len([p for p in new_products if p['category'] == 'Lưu trữ']) >= TARGET_COUNT['Lưu trữ']:
        break

storage_count = len([p for p in new_products if p['category'] == 'Lưu trữ'])
print(f"  Storage: {storage_count}")

# ════════════════════════════════════════════════════════════
# GENERATE ACCESSORIES  (~3500 target)
# ════════════════════════════════════════════════════════════
print("\n🎧 Generating accessories...")

ACC_PRODUCT_TEMPLATES = {
    "Tai nghe": {
        "brands": ["Apple","Samsung","Sony","JBL","Marshall","Bose","Edifier","Logitech","Sennheiser","Audio-Technica","Beyerdynamic","Jabra","Anker","SoundPeats","1MORE","Skullcandy","Beats","AKG","Final","Shure","KZ","Moondrop"],
        "series": ["Pro","Ultra","Max","Plus","SE","Lite","","Elite","Active","Sport","Studio","Classic"],
        "suffixes": ["ANC","Wireless","TWS","","BT","USB-C"],
    },
    "Bàn phím": {
        "brands": ["Logitech","Razer","Corsair","Keychron","Akko","Royal Kludge","Ducky","Leopold","Varmilo","NuPhy","Epomaker","FL ESPORTS","MOD","ASUS","HyperX","SteelSeries"],
        "series": ["Pro","Max","V2","V3","Plus","Mini","","S","X","Air","One"],
        "suffixes": ["Wireless","RGB","TKL","75%","65%","60%","Full-size","Hot-swap"],
    },
    "Chuột": {
        "brands": ["Logitech","Razer","Corsair","SteelSeries","HyperX","Pulsar","Lamzu","Ninjutso","Endgame Gear","Zowie","Roccat","Apple","ASUS","Glorious","Fantech"],
        "series": ["Pro","Ultra","V2","V3","Plus","Max","X","","Superlight","Wireless"],
        "suffixes": ["Gaming","Ergonomic","Wireless","","4K","8K"],
    },
    "Sạc & Cáp": {
        "brands": ["Anker","Apple","Samsung","Baseus","Ugreen","Belkin","Xiaomi","AUKEY","RavPower","Mophie","Spigen","Native Union","Twelve South"],
        "series": ["","Pro","Plus","Max","Mini","Nano","Prime","GaN"],
        "suffixes": ["USB-C","Lightning","MagSafe","PD","QC","Wireless",""],
    },
    "Loa": {
        "brands": ["JBL","Marshall","Bose","Sony","Harman Kardon","Apple","Bang & Olufsen","Sonos","KEF","Edifier","Creative","Ultimate Ears","Tribit","Anker"],
        "series": ["","Pro","Max","Plus","Mini","Ultra","Studio","One","Go","Move","Era"],
        "suffixes": ["Bluetooth","WiFi","Portable","","Smart","Party"],
    },
    "Webcam": {
        "brands": ["Logitech","Razer","Elgato","Obsbot","Insta360","AVerMedia","AUSDOM","Microsoft","HiHo","Poly"],
        "series": ["Pro","HD","Ultra","4K","","Studio","Stream"],
        "suffixes": ["","USB-C","AI","HDR","Autofocus"],
    },
    "Router": {
        "brands": ["ASUS","TP-Link","Netgear","Ubiquiti","Linksys","D-Link","Tenda","Xiaomi","Huawei","MikroTik"],
        "series": ["Pro","Max","AX","AXE","BE","","Mesh","Gaming","Ultra"],
        "suffixes": ["WiFi 6","WiFi 6E","WiFi 7","Mesh","","Tri-band","Dual-band"],
    },
    "Bao da / Ốp lưng": {
        "brands": ["Apple","Samsung","Spigen","UAG","Ringke","ESR","Nillkin","OtterBox","CASETiFY","Pitaka","Mous","UNIQ","Catalyst"],
        "series": ["","Ultra Hybrid","Monarch","Fusion","Clear","Slim","Tough","Nature","Air"],
        "suffixes": ["MagSafe","Clear","Silicone","Leather","Carbon","","Armor"],
    },
}

for acc_type, config in ACC_PRODUCT_TEMPLATES.items():
    for brand in config["brands"]:
        n_models = random.randint(5, 25)
        for _ in range(n_models):
            series = random.choice(config["series"])
            suffix = random.choice(config["suffixes"])
            ver = random.choice(["","","",str(random.randint(2,8)),"II","III","IV"])
            name = f"{brand} {series} {ver} {suffix}".replace("  "," ").strip()
            if name == brand:
                name = f"{brand} {acc_type} {ver}".strip()
            
            price = gen_price(100000, 15000000)
            orig = int(price * random.uniform(1.05, 1.25))
            
            specs = {"type": acc_type, "brand": brand, "connect": random.choice(["Bluetooth","USB-C","USB-A","Wireless","2.4GHz","–"]),
                     "feature": random.choice(["ANC","RGB","ergonomic","compact","portable","smart","–"])}
            add_product(name, "Phụ kiện", brand, price, orig, specs)
            
            if len([p for p in new_products if p['category'] == 'Phụ kiện']) >= TARGET_COUNT['Phụ kiện']:
                break
        if len([p for p in new_products if p['category'] == 'Phụ kiện']) >= TARGET_COUNT['Phụ kiện']:
            break
    if len([p for p in new_products if p['category'] == 'Phụ kiện']) >= TARGET_COUNT['Phụ kiện']:
        break

acc_count = len([p for p in new_products if p['category'] == 'Phụ kiện'])
print(f"  Accessories: {acc_count}")

# ════════════════════════════════════════════════════════════
# FILL REMAINING TO 20,000
# ════════════════════════════════════════════════════════════
print("\n🔄 Filling remaining slots...")

while len(new_products) < 20000:
    # Find category most under-target
    cat_counts = {}
    for p in new_products:
        cat_counts[p['category']] = cat_counts.get(p['category'], 0) + 1
    
    # Pick category with biggest gap
    gaps = {c: TARGET_COUNT.get(c, 0) - cat_counts.get(c, 0) for c in TARGET_COUNT}
    target_cat = max(gaps, key=gaps.get)
    
    # Create a variant from existing
    base_pool = [p for p in new_products if p['category'] == target_cat]
    if not base_pool:
        base_pool = new_products[:]
    base = random.choice(base_pool)
    
    suffix = random.choice([
        " - Phiên bản đặc biệt", " Limited Edition", " (Refurbished)",
        " Combo Edition", " Bundle Pack", " Special", " New", " 2025",
        " Pro+", " Max", " S", " V2", " Gen 2", " Upgraded"
    ])
    variant_name = base['name'] + suffix
    if variant_name in existing_names:
        continue
    
    price = int(base['price'] * random.uniform(0.7, 1.3))
    orig = int(price * random.uniform(1.05, 1.2))
    add_product(variant_name, base['category'], base['brand'], price, orig,
                base['specs'], base.get('colors'), TAG_POOLS.get(base['category'], ["chất lượng cao"]))

# Trim to exactly 20,000
new_products = new_products[:20000]

# ════════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════════
cat_counts = {}
for p in new_products:
    cat_counts[p['category']] = cat_counts.get(p['category'], 0) + 1

print(f"\n{'='*60}")
print(f"Total products: {len(new_products)}")
for c, n in sorted(cat_counts.items()):
    target = TARGET_COUNT.get(c, 0)
    print(f"  {c}: {n}/{target}")

with open(f'{DATA_DIR}/products.json', 'w', encoding='utf-8') as f:
    json.dump(new_products, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved {len(new_products)} products to {DATA_DIR}/products.json")
