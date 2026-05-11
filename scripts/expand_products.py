"""
Expand products.json from 70 to 1000 products.
Generates realistic Vietnamese e-commerce tech products.
"""
import json, random, copy, os

random.seed(2024)

DATA_DIR = 'd:/ok/data'

with open(f'{DATA_DIR}/products.json', encoding='utf-8') as f:
    existing = json.load(f)

print(f"Existing products: {len(existing)}")
max_id = max(p['id'] for p in existing)

# ────────────────────────────────────────────────────────────────
# PRODUCT TEMPLATES BY CATEGORY
# ────────────────────────────────────────────────────────────────

PHONE_BRANDS = {
    "Apple": {
        "models": [
            ("iPhone 16 Pro Max 256GB", 32990000, 36990000, {"screen":"6.9 inch Super Retina XDR OLED","chip":"A18 Pro","ram":"8GB","storage":"256GB","camera":"48MP + 12MP + 12MP","battery":"4685 mAh","os":"iOS 18"}),
            ("iPhone 16 Pro 128GB", 27990000, 30990000, {"screen":"6.3 inch Super Retina XDR OLED","chip":"A18 Pro","ram":"8GB","storage":"128GB","camera":"48MP + 12MP + 12MP","battery":"3577 mAh","os":"iOS 18"}),
            ("iPhone 16 Plus 128GB", 24990000, 27990000, {"screen":"6.7 inch Super Retina XDR OLED","chip":"A18","ram":"8GB","storage":"128GB","camera":"48MP + 12MP","battery":"4674 mAh","os":"iOS 18"}),
            ("iPhone 16 128GB", 21990000, 24990000, {"screen":"6.1 inch Super Retina XDR OLED","chip":"A18","ram":"8GB","storage":"128GB","camera":"48MP + 12MP","battery":"3561 mAh","os":"iOS 18"}),
            ("iPhone 15 128GB", 17990000, 22490000, {"screen":"6.1 inch Super Retina XDR OLED","chip":"A16 Bionic","ram":"6GB","storage":"128GB","camera":"48MP + 12MP","battery":"3349 mAh","os":"iOS 17"}),
            ("iPhone 15 Plus 256GB", 22990000, 27490000, {"screen":"6.7 inch Super Retina XDR OLED","chip":"A16 Bionic","ram":"6GB","storage":"256GB","camera":"48MP + 12MP","battery":"4383 mAh","os":"iOS 17"}),
            ("iPhone 14 128GB", 14990000, 19990000, {"screen":"6.1 inch Super Retina XDR OLED","chip":"A15 Bionic","ram":"6GB","storage":"128GB","camera":"12MP + 12MP","battery":"3279 mAh","os":"iOS 16"}),
            ("iPhone SE 4 128GB", 12990000, 14990000, {"screen":"6.1 inch OLED","chip":"A18","ram":"8GB","storage":"128GB","camera":"48MP","battery":"3279 mAh","os":"iOS 18"}),
        ],
        "colors": [["Titan Tự Nhiên","Titan Xanh","Titan Trắng","Titan Đen"],["Đen","Trắng","Xanh","Hồng"],["Xanh Dương","Vàng","Hồng","Xanh Lá","Đen"]],
        "tags_pool": ["cao cấp","flagship","chụp ảnh đẹp","gaming","pin trâu","FaceID","5G","Dynamic Island"]
    },
    "Samsung": {
        "models": [
            ("Samsung Galaxy S25 Ultra 256GB", 31990000, 35990000, {"screen":"6.9 inch Dynamic AMOLED 2X","chip":"Snapdragon 8 Elite","ram":"12GB","storage":"256GB","camera":"200MP + 50MP + 12MP + 10MP","battery":"5000 mAh","os":"Android 15"}),
            ("Samsung Galaxy S25+ 256GB", 25990000, 28990000, {"screen":"6.7 inch Dynamic AMOLED 2X","chip":"Snapdragon 8 Elite","ram":"12GB","storage":"256GB","camera":"50MP + 12MP + 10MP","battery":"4900 mAh","os":"Android 15"}),
            ("Samsung Galaxy S25 128GB", 20990000, 23990000, {"screen":"6.2 inch Dynamic AMOLED 2X","chip":"Snapdragon 8 Elite","ram":"8GB","storage":"128GB","camera":"50MP + 12MP + 10MP","battery":"4000 mAh","os":"Android 15"}),
            ("Samsung Galaxy Z Fold6 256GB", 41990000, 46990000, {"screen":"7.6 inch + 6.3 inch Dynamic AMOLED 2X","chip":"Snapdragon 8 Gen 3","ram":"12GB","storage":"256GB","camera":"50MP + 12MP + 10MP","battery":"4400 mAh","os":"Android 14"}),
            ("Samsung Galaxy Z Flip6 256GB", 25990000, 28990000, {"screen":"6.7 inch + 3.4 inch Dynamic AMOLED 2X","chip":"Snapdragon 8 Gen 3","ram":"12GB","storage":"256GB","camera":"50MP + 12MP","battery":"4000 mAh","os":"Android 14"}),
            ("Samsung Galaxy A55 5G 128GB", 9490000, 10990000, {"screen":"6.6 inch Super AMOLED","chip":"Exynos 1480","ram":"8GB","storage":"128GB","camera":"50MP + 12MP + 5MP","battery":"5000 mAh","os":"Android 14"}),
            ("Samsung Galaxy A35 5G 128GB", 7490000, 8990000, {"screen":"6.6 inch Super AMOLED","chip":"Exynos 1380","ram":"8GB","storage":"128GB","camera":"50MP + 8MP + 5MP","battery":"5000 mAh","os":"Android 14"}),
            ("Samsung Galaxy A15 128GB", 3990000, 4990000, {"screen":"6.5 inch Super AMOLED","chip":"Helio G99","ram":"6GB","storage":"128GB","camera":"50MP + 5MP + 2MP","battery":"5000 mAh","os":"Android 14"}),
            ("Samsung Galaxy M34 5G 128GB", 5990000, 7490000, {"screen":"6.5 inch Super AMOLED","chip":"Exynos 1280","ram":"6GB","storage":"128GB","camera":"50MP + 8MP + 2MP","battery":"6000 mAh","os":"Android 14"}),
        ],
        "colors": [["Xám Titan","Tím Titan","Vàng Titan","Đen Titan"],["Xanh","Đen","Kem","Tím"],["Đen","Trắng","Xanh Dương"]],
        "tags_pool": ["cao cấp","flagship","AI","Galaxy AI","camera 200MP","pin trâu","5G","gập"]
    },
    "Xiaomi": {
        "models": [
            ("Xiaomi 15 Pro 512GB", 21990000, 24990000, {"screen":"6.73 inch LTPO AMOLED","chip":"Snapdragon 8 Elite","ram":"16GB","storage":"512GB","camera":"50MP + 50MP + 50MP","battery":"6100 mAh","os":"Android 15"}),
            ("Xiaomi 15 256GB", 17990000, 19990000, {"screen":"6.36 inch LTPS AMOLED","chip":"Snapdragon 8 Elite","ram":"12GB","storage":"256GB","camera":"50MP + 50MP + 50MP","battery":"5400 mAh","os":"Android 15"}),
            ("Xiaomi 14 256GB", 15990000, 18990000, {"screen":"6.36 inch LTPO AMOLED","chip":"Snapdragon 8 Gen 3","ram":"12GB","storage":"256GB","camera":"50MP Leica × 3","battery":"4610 mAh","os":"Android 14"}),
            ("Redmi Note 14 Pro+ 5G 256GB", 8990000, 10490000, {"screen":"6.67 inch AMOLED","chip":"Snapdragon 7s Gen 3","ram":"8GB","storage":"256GB","camera":"200MP + 8MP + 2MP","battery":"5110 mAh","os":"Android 14"}),
            ("Redmi Note 14 Pro 128GB", 6990000, 8490000, {"screen":"6.67 inch AMOLED","chip":"Dimensity 7300","ram":"8GB","storage":"128GB","camera":"108MP + 8MP + 2MP","battery":"5500 mAh","os":"Android 14"}),
            ("Redmi Note 13 128GB", 4490000, 5490000, {"screen":"6.67 inch AMOLED","chip":"Snapdragon 685","ram":"6GB","storage":"128GB","camera":"108MP + 8MP + 2MP","battery":"5000 mAh","os":"Android 13"}),
            ("Xiaomi Poco X6 Pro 256GB", 7990000, 9490000, {"screen":"6.67 inch AMOLED","chip":"Dimensity 8300 Ultra","ram":"8GB","storage":"256GB","camera":"64MP + 8MP + 2MP","battery":"5000 mAh","os":"Android 14"}),
            ("Xiaomi Poco F6 256GB", 8990000, 10990000, {"screen":"6.67 inch AMOLED","chip":"Snapdragon 8s Gen 3","ram":"8GB","storage":"256GB","camera":"50MP + 8MP","battery":"5000 mAh","os":"Android 14"}),
        ],
        "colors": [["Đen","Trắng","Xanh"],["Tím","Xanh Lá","Đen"],["Bạc","Đen","Xanh Dương"]],
        "tags_pool": ["giá tốt","camera Leica","sạc nhanh","AMOLED","5G","hiệu năng cao"]
    },
    "OPPO": {
        "models": [
            ("OPPO Find X7 Ultra 256GB", 24990000, 28990000, {"screen":"6.82 inch LTPO AMOLED","chip":"Snapdragon 8 Gen 3","ram":"16GB","storage":"256GB","camera":"50MP Hasselblad × 4","battery":"5400 mAh","os":"Android 14"}),
            ("OPPO Find N3 Flip 256GB", 19990000, 22990000, {"screen":"6.8 inch + 3.26 inch AMOLED","chip":"Dimensity 9200","ram":"12GB","storage":"256GB","camera":"50MP + 32MP + 48MP","battery":"4300 mAh","os":"Android 13"}),
            ("OPPO Reno12 Pro 5G 256GB", 11990000, 13990000, {"screen":"6.7 inch AMOLED","chip":"Dimensity 9200+","ram":"12GB","storage":"256GB","camera":"50MP + 50MP + 8MP","battery":"5000 mAh","os":"Android 14"}),
            ("OPPO Reno12 5G 256GB", 9990000, 11490000, {"screen":"6.7 inch AMOLED","chip":"Dimensity 7300 Energy","ram":"12GB","storage":"256GB","camera":"50MP + 8MP + 2MP","battery":"5000 mAh","os":"Android 14"}),
            ("OPPO A79 5G 128GB", 5990000, 6990000, {"screen":"6.72 inch LCD","chip":"Dimensity 6020","ram":"8GB","storage":"128GB","camera":"50MP + 2MP","battery":"5000 mAh","os":"Android 13"}),
            ("OPPO A58 128GB", 4490000, 5490000, {"screen":"6.72 inch LCD","chip":"Helio G85","ram":"6GB","storage":"128GB","camera":"50MP + 2MP","battery":"5000 mAh","os":"Android 13"}),
            ("OPPO A18 128GB", 3290000, 3990000, {"screen":"6.56 inch LCD","chip":"Helio G85","ram":"4GB","storage":"128GB","camera":"8MP + 2MP","battery":"5000 mAh","os":"Android 13"}),
        ],
        "colors": [["Đen","Xanh Dương","Tím"],["Vàng","Đen","Bạc"],["Xanh Lá","Đen","Trắng"]],
        "tags_pool": ["camera AI","sạc nhanh VOOC","mỏng nhẹ","AMOLED","5G"]
    },
    "vivo": {
        "models": [
            ("vivo X200 Pro 256GB", 22990000, 25990000, {"screen":"6.78 inch LTPO AMOLED","chip":"Dimensity 9400","ram":"16GB","storage":"256GB","camera":"50MP ZEISS × 3","battery":"6000 mAh","os":"Android 15"}),
            ("vivo X100 Ultra 512GB", 26990000, 29990000, {"screen":"6.78 inch LTPO AMOLED","chip":"Snapdragon 8 Gen 3","ram":"16GB","storage":"512GB","camera":"50MP ZEISS × 3","battery":"5500 mAh","os":"Android 14"}),
            ("vivo V40 5G 256GB", 10990000, 12490000, {"screen":"6.78 inch AMOLED","chip":"Snapdragon 7 Gen 3","ram":"12GB","storage":"256GB","camera":"50MP + 50MP","battery":"5500 mAh","os":"Android 14"}),
            ("vivo V30e 5G 256GB", 8490000, 9990000, {"screen":"6.78 inch AMOLED","chip":"Snapdragon 6 Gen 1","ram":"12GB","storage":"256GB","camera":"50MP + 8MP","battery":"5500 mAh","os":"Android 14"}),
            ("vivo Y36 128GB", 4290000, 5290000, {"screen":"6.64 inch LCD","chip":"Snapdragon 680","ram":"8GB","storage":"128GB","camera":"50MP + 2MP","battery":"5000 mAh","os":"Android 13"}),
        ],
        "colors": [["Đen","Xanh","Tím"],["Trắng","Đen","Xanh Dương"]],
        "tags_pool": ["camera ZEISS","sạc nhanh","mỏng nhẹ","AMOLED","5G"]
    },
    "realme": {
        "models": [
            ("realme GT6 256GB", 11990000, 13990000, {"screen":"6.78 inch LTPO AMOLED","chip":"Snapdragon 8s Gen 3","ram":"12GB","storage":"256GB","camera":"50MP + 8MP + 2MP","battery":"5500 mAh","os":"Android 14"}),
            ("realme 12 Pro+ 5G 256GB", 10990000, 12990000, {"screen":"6.7 inch AMOLED","chip":"Snapdragon 7s Gen 2","ram":"8GB","storage":"256GB","camera":"50MP + 64MP + 8MP","battery":"5000 mAh","os":"Android 14"}),
            ("realme 12 Pro 128GB", 8490000, 9990000, {"screen":"6.7 inch AMOLED","chip":"Snapdragon 6 Gen 1","ram":"8GB","storage":"128GB","camera":"50MP + 32MP + 8MP","battery":"5000 mAh","os":"Android 14"}),
            ("realme C67 128GB", 3790000, 4490000, {"screen":"6.72 inch LCD","chip":"Snapdragon 685","ram":"6GB","storage":"128GB","camera":"108MP + 2MP","battery":"5000 mAh","os":"Android 13"}),
            ("realme Note 60 64GB", 2490000, 2990000, {"screen":"6.74 inch LCD","chip":"Unisoc T612","ram":"4GB","storage":"64GB","camera":"32MP + 2MP","battery":"5000 mAh","os":"Android 14"}),
        ],
        "colors": [["Đen","Xanh","Cam"],["Trắng","Đen"]],
        "tags_pool": ["giá tốt","sạc nhanh","AMOLED","5G","hiệu năng cao","gaming"]
    },
    "Google": {
        "models": [
            ("Google Pixel 9 Pro 256GB", 24990000, 27990000, {"screen":"6.3 inch LTPO OLED","chip":"Tensor G4","ram":"16GB","storage":"256GB","camera":"50MP + 48MP + 48MP","battery":"4700 mAh","os":"Android 15"}),
            ("Google Pixel 9 128GB", 18990000, 21990000, {"screen":"6.3 inch OLED","chip":"Tensor G4","ram":"12GB","storage":"128GB","camera":"50MP + 48MP","battery":"4700 mAh","os":"Android 15"}),
            ("Google Pixel 8a 128GB", 11990000, 13990000, {"screen":"6.1 inch OLED","chip":"Tensor G3","ram":"8GB","storage":"128GB","camera":"64MP + 13MP","battery":"4492 mAh","os":"Android 14"}),
        ],
        "colors": [["Đen Obsidian","Trắng Porcelain","Xanh Hazel"],["Xanh Mint","Đen","Trắng"]],
        "tags_pool": ["AI","camera AI","Google AI","stock Android","cập nhật lâu"]
    },
    "Nothing": {
        "models": [
            ("Nothing Phone (2a) 256GB", 8990000, 10490000, {"screen":"6.7 inch AMOLED","chip":"Dimensity 7200 Pro","ram":"8GB","storage":"256GB","camera":"50MP + 50MP","battery":"5000 mAh","os":"Android 14"}),
            ("Nothing Phone (2) 256GB", 12990000, 14990000, {"screen":"6.7 inch LTPO OLED","chip":"Snapdragon 8+ Gen 1","ram":"12GB","storage":"256GB","camera":"50MP + 50MP","battery":"4700 mAh","os":"Android 13"}),
        ],
        "colors": [["Đen","Trắng"],["Xám","Trắng"]],
        "tags_pool": ["thiết kế độc lạ","Glyph Interface","AMOLED"]
    },
    "OnePlus": {
        "models": [
            ("OnePlus 12 256GB", 19990000, 22990000, {"screen":"6.82 inch LTPO AMOLED","chip":"Snapdragon 8 Gen 3","ram":"12GB","storage":"256GB","camera":"50MP + 64MP + 48MP","battery":"5400 mAh","os":"Android 14"}),
            ("OnePlus Nord CE4 128GB", 7490000, 8990000, {"screen":"6.7 inch AMOLED","chip":"Snapdragon 7 Gen 3","ram":"8GB","storage":"128GB","camera":"50MP + 8MP","battery":"5500 mAh","os":"Android 14"}),
        ],
        "colors": [["Đen","Xanh"],["Xám","Đen"]],
        "tags_pool": ["sạc nhanh 100W","AMOLED","OxygenOS","hiệu năng cao"]
    },
}

LAPTOP_BRANDS = {
    "Apple": {
        "models": [
            ("MacBook Pro 16 M4 Pro 512GB", 62990000, 67990000, {"screen":"16.2 inch Liquid Retina XDR","chip":"Apple M4 Pro","ram":"24GB","storage":"512GB SSD","gpu":"18-core GPU","battery":"22 giờ","os":"macOS Sequoia"}),
            ("MacBook Pro 14 M4 512GB", 39990000, 44990000, {"screen":"14.2 inch Liquid Retina XDR","chip":"Apple M4","ram":"16GB","storage":"512GB SSD","gpu":"10-core GPU","battery":"24 giờ","os":"macOS Sequoia"}),
            ("MacBook Pro 14 M4 Max 1TB", 89990000, 96990000, {"screen":"14.2 inch Liquid Retina XDR","chip":"Apple M4 Max","ram":"36GB","storage":"1TB SSD","gpu":"40-core GPU","battery":"18 giờ","os":"macOS Sequoia"}),
            ("MacBook Air 15 M3 256GB", 32990000, 36990000, {"screen":"15.3 inch Liquid Retina","chip":"Apple M3","ram":"8GB","storage":"256GB SSD","gpu":"10-core GPU","battery":"18 giờ","os":"macOS Sonoma"}),
            ("MacBook Air 13 M3 256GB", 27490000, 32490000, {"screen":"13.6 inch Liquid Retina","chip":"Apple M3","ram":"8GB","storage":"256GB SSD","gpu":"10-core GPU","battery":"18 giờ","os":"macOS Sonoma"}),
            ("MacBook Air 13 M2 256GB", 22490000, 27490000, {"screen":"13.6 inch Liquid Retina","chip":"Apple M2","ram":"8GB","storage":"256GB SSD","gpu":"8-core GPU","battery":"18 giờ","os":"macOS Sonoma"}),
        ],
        "colors": [["Bạc","Xám Không Gian","Vàng Sao","Đen Không Gian"],["Bạc","Xám","Vàng","Xanh Đêm"]],
        "tags_pool": ["cao cấp","mỏng nhẹ","chip Apple Silicon","pin trâu","Retina","macOS"]
    },
    "Dell": {
        "models": [
            ("Dell XPS 14 9440 Core Ultra 7 512GB", 42990000, 47990000, {"screen":"14.5 inch 3.2K OLED","chip":"Intel Core Ultra 7 155H","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"70Wh","os":"Windows 11"}),
            ("Dell XPS 16 9640 Core Ultra 9 1TB", 54990000, 59990000, {"screen":"16.3 inch 4K+ OLED","chip":"Intel Core Ultra 9 185H","ram":"32GB","storage":"1TB SSD","gpu":"NVIDIA RTX 4060","battery":"99.5Wh","os":"Windows 11"}),
            ("Dell XPS 13 Plus 9320 512GB", 32990000, 37990000, {"screen":"13.4 inch 3.5K OLED","chip":"Intel Core i7-1360P","ram":"16GB","storage":"512GB SSD","gpu":"Intel Iris Xe","battery":"55Wh","os":"Windows 11"}),
            ("Dell Inspiron 16 5630 512GB", 18990000, 21990000, {"screen":"16 inch FHD+","chip":"Intel Core i7-1360P","ram":"16GB","storage":"512GB SSD","gpu":"Intel Iris Xe","battery":"54Wh","os":"Windows 11"}),
            ("Dell Inspiron 15 3530 256GB", 12990000, 15990000, {"screen":"15.6 inch FHD","chip":"Intel Core i5-1335U","ram":"8GB","storage":"256GB SSD","gpu":"Intel UHD","battery":"41Wh","os":"Windows 11"}),
            ("Dell Latitude 5540 512GB", 28990000, 32990000, {"screen":"15.6 inch FHD","chip":"Intel Core i7-1365U","ram":"16GB","storage":"512GB SSD","gpu":"Intel Iris Xe","battery":"58Wh","os":"Windows 11 Pro"}),
            ("Dell Vostro 3520 256GB", 11990000, 14990000, {"screen":"15.6 inch FHD","chip":"Intel Core i5-1235U","ram":"8GB","storage":"256GB SSD","gpu":"Intel UHD","battery":"41Wh","os":"Windows 11"}),
            ("Dell G16 7630 RTX 4060 512GB", 32990000, 37990000, {"screen":"16 inch QHD+ 165Hz","chip":"Intel Core i7-13650HX","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4060 8GB","battery":"86Wh","os":"Windows 11"}),
        ],
        "colors": [["Bạc","Xám"],["Đen","Bạc","Xám"]],
        "tags_pool": ["cao cấp","mỏng nhẹ","doanh nhân","XPS","OLED","Windows"]
    },
    "Lenovo": {
        "models": [
            ("Lenovo ThinkPad X1 Carbon Gen 12 512GB", 42990000, 47990000, {"screen":"14 inch 2.8K OLED","chip":"Intel Core Ultra 7 155U","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"57Wh","os":"Windows 11 Pro"}),
            ("Lenovo ThinkPad T14s Gen 5 256GB", 28990000, 32990000, {"screen":"14 inch WUXGA","chip":"Intel Core Ultra 5 125U","ram":"16GB","storage":"256GB SSD","gpu":"Intel Arc Graphics","battery":"58Wh","os":"Windows 11 Pro"}),
            ("Lenovo IdeaPad Slim 5 14 512GB", 16990000, 19990000, {"screen":"14 inch 2.8K OLED","chip":"Intel Core i7-1355U","ram":"16GB","storage":"512GB SSD","gpu":"Intel Iris Xe","battery":"56.5Wh","os":"Windows 11"}),
            ("Lenovo IdeaPad 3 15 256GB", 10490000, 12990000, {"screen":"15.6 inch FHD","chip":"Intel Core i5-1235U","ram":"8GB","storage":"256GB SSD","gpu":"Intel UHD","battery":"45Wh","os":"Windows 11"}),
            ("Lenovo Yoga Slim 7i 14 512GB", 24990000, 28990000, {"screen":"14 inch 2.8K OLED","chip":"Intel Core Ultra 7 155H","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"70Wh","os":"Windows 11"}),
            ("Lenovo Legion 5 Pro 16 RTX 4070 512GB", 38990000, 43990000, {"screen":"16 inch WQXGA 165Hz","chip":"AMD Ryzen 7 7745HX","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4070 8GB","battery":"80Wh","os":"Windows 11"}),
            ("Lenovo Legion 5i 15 RTX 4060 512GB", 29990000, 34990000, {"screen":"15.6 inch FHD 144Hz","chip":"Intel Core i7-13650HX","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4060 8GB","battery":"80Wh","os":"Windows 11"}),
            ("Lenovo LOQ 15 RTX 4050 512GB", 19990000, 23990000, {"screen":"15.6 inch FHD 144Hz","chip":"Intel Core i5-13450HX","ram":"8GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4050 6GB","battery":"60Wh","os":"Windows 11"}),
            ("Lenovo ThinkBook 16 Gen 6 512GB", 18990000, 21990000, {"screen":"16 inch WUXGA","chip":"Intel Core i7-1360P","ram":"16GB","storage":"512GB SSD","gpu":"Intel Iris Xe","battery":"62Wh","os":"Windows 11"}),
        ],
        "colors": [["Xám","Đen"],["Đen","Xám Bạc"],["Xám Bão","Xanh Đêm"]],
        "tags_pool": ["doanh nhân","ThinkPad","mỏng nhẹ","gaming","bàn phím tốt","bền bỉ"]
    },
    "ASUS": {
        "models": [
            ("ASUS ZenBook 14 OLED UX3405 512GB", 26990000, 30990000, {"screen":"14 inch 3K OLED","chip":"Intel Core Ultra 7 155H","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"75Wh","os":"Windows 11"}),
            ("ASUS ZenBook S 14 UX5406 1TB", 38990000, 43990000, {"screen":"14 inch 3K OLED","chip":"Intel Core Ultra 9 285H","ram":"32GB","storage":"1TB SSD","gpu":"Intel Arc 140V","battery":"72Wh","os":"Windows 11"}),
            ("ASUS Vivobook 15 OLED M3504 512GB", 16990000, 19990000, {"screen":"15.6 inch FHD OLED","chip":"AMD Ryzen 7 7730U","ram":"16GB","storage":"512GB SSD","gpu":"AMD Radeon","battery":"50Wh","os":"Windows 11"}),
            ("ASUS Vivobook 14 256GB", 10990000, 13990000, {"screen":"14 inch FHD","chip":"Intel Core i5-1335U","ram":"8GB","storage":"256GB SSD","gpu":"Intel Iris Xe","battery":"42Wh","os":"Windows 11"}),
            ("ASUS ROG Strix G16 RTX 4070 512GB", 39990000, 44990000, {"screen":"16 inch QHD 240Hz","chip":"Intel Core i9-14900HX","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4070 8GB","battery":"90Wh","os":"Windows 11"}),
            ("ASUS ROG Strix G15 RTX 4060 512GB", 29990000, 34990000, {"screen":"15.6 inch FHD 144Hz","chip":"AMD Ryzen 9 7845HX","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4060 8GB","battery":"76Wh","os":"Windows 11"}),
            ("ASUS TUF Gaming A15 RTX 4050 512GB", 21990000, 25990000, {"screen":"15.6 inch FHD 144Hz","chip":"AMD Ryzen 7 7735HS","ram":"8GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4050 6GB","battery":"76Wh","os":"Windows 11"}),
            ("ASUS ROG Zephyrus G14 RTX 4060 512GB", 34990000, 39990000, {"screen":"14 inch QHD+ 165Hz","chip":"AMD Ryzen 9 8945HS","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4060 8GB","battery":"73Wh","os":"Windows 11"}),
            ("ASUS ExpertBook B9 OLED 512GB", 34990000, 39990000, {"screen":"14 inch 2.8K OLED","chip":"Intel Core Ultra 7 155U","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"63Wh","os":"Windows 11 Pro"}),
        ],
        "colors": [["Xám","Đen","Xanh"],["Đen Eclipse","Trắng Moonlight"],["Xám Volt","Đen"]],
        "tags_pool": ["OLED","mỏng nhẹ","gaming","ROG","ZenBook","hiệu năng cao","bền bỉ"]
    },
    "HP": {
        "models": [
            ("HP Spectre x360 14 OLED 512GB", 38990000, 43990000, {"screen":"14 inch 2.8K OLED","chip":"Intel Core Ultra 7 155H","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"68Wh","os":"Windows 11"}),
            ("HP Envy x360 15 512GB", 24990000, 28990000, {"screen":"15.6 inch FHD OLED","chip":"AMD Ryzen 7 8840HS","ram":"16GB","storage":"512GB SSD","gpu":"AMD Radeon 780M","battery":"64Wh","os":"Windows 11"}),
            ("HP Pavilion 15 256GB", 12990000, 15990000, {"screen":"15.6 inch FHD","chip":"Intel Core i5-1335U","ram":"8GB","storage":"256GB SSD","gpu":"Intel Iris Xe","battery":"41Wh","os":"Windows 11"}),
            ("HP Pavilion 14 Plus 512GB", 17990000, 20990000, {"screen":"14 inch 2.8K OLED","chip":"Intel Core i7-1355U","ram":"16GB","storage":"512GB SSD","gpu":"Intel Iris Xe","battery":"51Wh","os":"Windows 11"}),
            ("HP Victus 16 RTX 4060 512GB", 24990000, 28990000, {"screen":"16.1 inch FHD 144Hz","chip":"Intel Core i7-13700H","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4060 8GB","battery":"70Wh","os":"Windows 11"}),
            ("HP OMEN 16 RTX 4070 1TB", 38990000, 43990000, {"screen":"16.1 inch QHD 165Hz","chip":"Intel Core i9-13900HX","ram":"16GB","storage":"1TB SSD","gpu":"NVIDIA RTX 4070 8GB","battery":"83Wh","os":"Windows 11"}),
            ("HP 15s 256GB", 8990000, 10990000, {"screen":"15.6 inch FHD","chip":"Intel Core i3-1315U","ram":"8GB","storage":"256GB SSD","gpu":"Intel UHD","battery":"41Wh","os":"Windows 11"}),
            ("HP EliteBook 840 G10 512GB", 32990000, 37990000, {"screen":"14 inch WUXGA","chip":"Intel Core i7-1365U","ram":"16GB","storage":"512GB SSD","gpu":"Intel Iris Xe","battery":"51Wh","os":"Windows 11 Pro"}),
        ],
        "colors": [["Bạc","Đen","Xanh"],["Đen Mica","Bạc"],["Xám Tối","Trắng"]],
        "tags_pool": ["doanh nhân","mỏng nhẹ","OLED","gaming","Spectre","Pavilion"]
    },
    "Acer": {
        "models": [
            ("Acer Swift Go 14 OLED 512GB", 18990000, 21990000, {"screen":"14 inch 2.8K OLED","chip":"Intel Core Ultra 5 125H","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"65Wh","os":"Windows 11"}),
            ("Acer Aspire 5 15 256GB", 11490000, 13990000, {"screen":"15.6 inch FHD","chip":"Intel Core i5-1335U","ram":"8GB","storage":"256GB SSD","gpu":"Intel Iris Xe","battery":"50Wh","os":"Windows 11"}),
            ("Acer Aspire 3 15 256GB", 8490000, 10490000, {"screen":"15.6 inch FHD","chip":"Intel Core i3-1315U","ram":"8GB","storage":"256GB SSD","gpu":"Intel UHD","battery":"36.7Wh","os":"Windows 11"}),
            ("Acer Predator Helios Neo 16 RTX 4070 512GB", 36990000, 41990000, {"screen":"16 inch WQXGA 165Hz","chip":"Intel Core i9-14900HX","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4070 8GB","battery":"76Wh","os":"Windows 11"}),
            ("Acer Nitro V 15 RTX 4050 512GB", 19990000, 23990000, {"screen":"15.6 inch FHD 144Hz","chip":"Intel Core i5-13420H","ram":"8GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4050 6GB","battery":"57Wh","os":"Windows 11"}),
            ("Acer Nitro 5 RTX 3050 512GB", 16990000, 19990000, {"screen":"15.6 inch FHD 144Hz","chip":"Intel Core i5-12500H","ram":"8GB","storage":"512GB SSD","gpu":"NVIDIA RTX 3050 4GB","battery":"57Wh","os":"Windows 11"}),
        ],
        "colors": [["Bạc","Đen"],["Đen","Xám"]],
        "tags_pool": ["giá tốt","gaming","OLED","mỏng nhẹ","Predator","Nitro"]
    },
    "MSI": {
        "models": [
            ("MSI Creator 16 HX RTX 4070 1TB", 52990000, 57990000, {"screen":"16 inch Mini LED QHD+ 165Hz","chip":"Intel Core i9-14900HX","ram":"32GB","storage":"1TB SSD","gpu":"NVIDIA RTX 4070 8GB","battery":"99.9Wh","os":"Windows 11 Pro"}),
            ("MSI Prestige 14 EVO 512GB", 24990000, 28990000, {"screen":"14 inch FHD+","chip":"Intel Core Ultra 7 155H","ram":"16GB","storage":"512GB SSD","gpu":"Intel Arc Graphics","battery":"72Wh","os":"Windows 11"}),
            ("MSI Stealth 16 AI Studio RTX 4070 1TB", 48990000, 53990000, {"screen":"16 inch QHD+ 240Hz OLED","chip":"Intel Core Ultra 9 185H","ram":"32GB","storage":"1TB SSD","gpu":"NVIDIA RTX 4070 8GB","battery":"99.9Wh","os":"Windows 11"}),
            ("MSI Katana 15 RTX 4060 512GB", 24990000, 28990000, {"screen":"15.6 inch FHD 144Hz","chip":"Intel Core i7-13620H","ram":"16GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4060 8GB","battery":"53.5Wh","os":"Windows 11"}),
            ("MSI Thin 15 RTX 4050 512GB", 18990000, 21990000, {"screen":"15.6 inch FHD 144Hz","chip":"Intel Core i5-13420H","ram":"8GB","storage":"512GB SSD","gpu":"NVIDIA RTX 4050 6GB","battery":"53.5Wh","os":"Windows 11"}),
            ("MSI Modern 14 256GB", 11990000, 14990000, {"screen":"14 inch FHD","chip":"Intel Core i5-1335U","ram":"8GB","storage":"256GB SSD","gpu":"Intel Iris Xe","battery":"39.3Wh","os":"Windows 11"}),
        ],
        "colors": [["Đen","Xám"],["Đen Core","Bạc Urban"]],
        "tags_pool": ["gaming","creator","RTX","MSI","hiệu năng cao","Mini LED"]
    },
}

TABLET_BRANDS = {
    "Apple": {
        "models": [
            ("iPad Pro M4 11 inch 256GB WiFi", 27990000, 30990000, {"screen":"11 inch Liquid Retina XDR OLED","chip":"Apple M4","ram":"8GB","storage":"256GB","camera":"12MP + 10MP LiDAR","battery":"10 giờ","os":"iPadOS 18"}),
            ("iPad Pro M4 13 inch 256GB WiFi", 34990000, 38990000, {"screen":"13 inch Liquid Retina XDR OLED","chip":"Apple M4","ram":"8GB","storage":"256GB","camera":"12MP + 10MP LiDAR","battery":"10 giờ","os":"iPadOS 18"}),
            ("iPad Air M2 11 inch 128GB WiFi", 16490000, 18990000, {"screen":"11 inch Liquid Retina","chip":"Apple M2","ram":"8GB","storage":"128GB","camera":"12MP","battery":"10 giờ","os":"iPadOS 17"}),
            ("iPad Air M2 13 inch 128GB WiFi", 20990000, 23990000, {"screen":"13 inch Liquid Retina","chip":"Apple M2","ram":"8GB","storage":"128GB","camera":"12MP","battery":"10 giờ","os":"iPadOS 17"}),
            ("iPad 10 64GB WiFi", 8490000, 10490000, {"screen":"10.9 inch Liquid Retina","chip":"A14 Bionic","ram":"4GB","storage":"64GB","camera":"12MP","battery":"10 giờ","os":"iPadOS 16"}),
            ("iPad mini 7 128GB WiFi", 12990000, 14990000, {"screen":"8.3 inch Liquid Retina","chip":"A17 Pro","ram":"8GB","storage":"128GB","camera":"12MP","battery":"10 giờ","os":"iPadOS 18"}),
        ],
        "colors": [["Bạc","Xám Không Gian"],["Xanh","Tím","Vàng Sao","Xám"]],
        "tags_pool": ["cao cấp","Apple Pencil","M4","mỏng nhẹ","Retina","iPadOS"]
    },
    "Samsung": {
        "models": [
            ("Samsung Galaxy Tab S10 Ultra 256GB WiFi", 28990000, 32990000, {"screen":"14.6 inch Dynamic AMOLED 2X","chip":"Dimensity 9300+","ram":"12GB","storage":"256GB","camera":"13MP + 8MP","battery":"11200 mAh","os":"Android 14"}),
            ("Samsung Galaxy Tab S10+ 256GB WiFi", 23990000, 26990000, {"screen":"12.4 inch Dynamic AMOLED 2X","chip":"Dimensity 9300+","ram":"12GB","storage":"256GB","camera":"13MP + 8MP","battery":"10090 mAh","os":"Android 14"}),
            ("Samsung Galaxy Tab S9 FE 128GB WiFi", 9490000, 11000000, {"screen":"10.9 inch LCD","chip":"Exynos 1380","ram":"6GB","storage":"128GB","camera":"8MP","battery":"8000 mAh","os":"Android 13"}),
            ("Samsung Galaxy Tab A9+ 64GB WiFi", 6490000, 7990000, {"screen":"11 inch LCD","chip":"Snapdragon 695","ram":"4GB","storage":"64GB","camera":"8MP","battery":"7040 mAh","os":"Android 13"}),
        ],
        "colors": [["Xám Graphite","Bạc"],["Xám","Xanh Mint","Bạc"]],
        "tags_pool": ["S Pen","Galaxy AI","AMOLED","pin trâu","màn hình lớn"]
    },
    "Xiaomi": {
        "models": [
            ("Xiaomi Pad 6S Pro 256GB", 10990000, 12990000, {"screen":"12.4 inch LCD 144Hz","chip":"Snapdragon 8 Gen 2","ram":"8GB","storage":"256GB","camera":"50MP","battery":"10000 mAh","os":"Android 14"}),
            ("Xiaomi Pad 6 128GB", 6490000, 7990000, {"screen":"11 inch LCD 144Hz","chip":"Snapdragon 870","ram":"6GB","storage":"128GB","camera":"13MP","battery":"8840 mAh","os":"Android 13"}),
            ("Xiaomi Redmi Pad SE 128GB", 3990000, 4990000, {"screen":"11 inch LCD","chip":"Snapdragon 680","ram":"4GB","storage":"128GB","camera":"8MP","battery":"8000 mAh","os":"Android 13"}),
        ],
        "colors": [["Đen","Xanh"],["Xám","Xanh Dương"]],
        "tags_pool": ["giá tốt","144Hz","pin khủng","giải trí"]
    },
}

MONITOR_BRANDS = {
    "LG": {
        "models": [
            ("LG UltraGear 27GR95QE 27 inch OLED QHD 240Hz", 18990000, 21990000, {"panel":"27 inch OLED","resolution":"2560x1440 QHD","refresh":"240Hz","response":"0.03ms","hdr":"HDR10","ports":"HDMI 2.1 x2, DP 1.4"}),
            ("LG UltraFine 32UN880 32 inch 4K IPS Ergo", 16990000, 19990000, {"panel":"32 inch IPS","resolution":"3840x2160 4K","refresh":"60Hz","response":"5ms","hdr":"HDR10","ports":"HDMI x2, DP, USB-C 60W"}),
            ("LG 27UP850N 27 inch 4K IPS USB-C", 9990000, 11990000, {"panel":"27 inch IPS","resolution":"3840x2160 4K","refresh":"60Hz","response":"5ms","hdr":"HDR400","ports":"HDMI x2, DP, USB-C 96W"}),
            ("LG 24MP400 24 inch FHD IPS", 2990000, 3590000, {"panel":"24 inch IPS","resolution":"1920x1080 FHD","refresh":"75Hz","response":"5ms","hdr":"No","ports":"HDMI, VGA"}),
            ("LG UltraWide 34WP85C 34 inch QHD IPS Curved", 13990000, 16990000, {"panel":"34 inch IPS Curved","resolution":"3440x1440 UWQHD","refresh":"60Hz","response":"5ms","hdr":"HDR10","ports":"HDMI x2, DP, USB-C 90W"}),
        ],
        "colors": [["Đen"],["Đen","Trắng"]],
        "tags_pool": ["OLED","4K","gaming","UltraGear","UltraFine","USB-C","HDR"]
    },
    "Samsung": {
        "models": [
            ("Samsung Odyssey G9 49 inch DQHD 240Hz", 32990000, 37990000, {"panel":"49 inch VA Curved","resolution":"5120x1440 DQHD","refresh":"240Hz","response":"1ms","hdr":"HDR1000","ports":"HDMI 2.1 x2, DP 1.4 x2"}),
            ("Samsung Odyssey OLED G8 34 inch QHD 175Hz", 24990000, 28990000, {"panel":"34 inch OLED","resolution":"3440x1440 UWQHD","refresh":"175Hz","response":"0.1ms","hdr":"HDR True Black 400","ports":"HDMI 2.1, DP 1.4, USB-C"}),
            ("Samsung ViewFinity S8 27 inch 4K IPS", 8990000, 10990000, {"panel":"27 inch IPS","resolution":"3840x2160 4K","refresh":"60Hz","response":"5ms","hdr":"HDR600","ports":"HDMI, DP, USB-C 90W"}),
            ("Samsung 27 inch FHD IPS 75Hz LS27C360", 3490000, 4290000, {"panel":"27 inch IPS","resolution":"1920x1080 FHD","refresh":"75Hz","response":"5ms","hdr":"No","ports":"HDMI, VGA"}),
            ("Samsung Smart Monitor M8 32 inch 4K", 11990000, 13990000, {"panel":"32 inch VA","resolution":"3840x2160 4K","refresh":"60Hz","response":"4ms","hdr":"HDR10+","ports":"HDMI, USB-C, WiFi, Bluetooth"}),
        ],
        "colors": [["Trắng","Đen"],["Đen"]],
        "tags_pool": ["gaming","Odyssey","4K","OLED","Curved","Smart Monitor"]
    },
    "Dell": {
        "models": [
            ("Dell UltraSharp U2724D 27 inch QHD IPS USB-C", 11990000, 13990000, {"panel":"27 inch IPS Black","resolution":"2560x1440 QHD","refresh":"120Hz","response":"5ms","hdr":"HDR400","ports":"HDMI, DP, USB-C 90W"}),
            ("Dell UltraSharp U3224KB 32 inch 6K IPS", 42990000, 48990000, {"panel":"32 inch IPS Black","resolution":"6144x3456 6K","refresh":"60Hz","response":"5ms","hdr":"HDR600","ports":"Thunderbolt 4, HDMI, USB-C"}),
            ("Dell S2722QC 27 inch 4K IPS USB-C", 7490000, 8990000, {"panel":"27 inch IPS","resolution":"3840x2160 4K","refresh":"60Hz","response":"4ms","hdr":"HDR400","ports":"HDMI x2, USB-C 65W"}),
            ("Dell P2425H 24 inch FHD IPS", 4490000, 5490000, {"panel":"24 inch IPS","resolution":"1920x1080 FHD","refresh":"100Hz","response":"5ms","hdr":"No","ports":"HDMI, DP, VGA, USB Hub"}),
        ],
        "colors": [["Đen","Bạc"],["Đen"]],
        "tags_pool": ["chuyên nghiệp","UltraSharp","USB-C","4K","6K","màu chuẩn"]
    },
    "ASUS": {
        "models": [
            ("ASUS ProArt PA32UCXR 32 inch 4K Mini LED", 42990000, 48990000, {"panel":"32 inch IPS Mini LED","resolution":"3840x2160 4K","refresh":"120Hz","response":"5ms","hdr":"HDR1600","ports":"HDMI 2.1 x2, DP 1.4, Thunderbolt 4"}),
            ("ASUS ROG Swift PG27AQDM 27 inch QHD OLED 240Hz", 19990000, 22990000, {"panel":"27 inch OLED","resolution":"2560x1440 QHD","refresh":"240Hz","response":"0.03ms","hdr":"HDR True Black 400","ports":"HDMI 2.0, DP 1.4, USB Hub"}),
            ("ASUS VG279Q1A 27 inch FHD IPS 165Hz", 4990000, 5990000, {"panel":"27 inch IPS","resolution":"1920x1080 FHD","refresh":"165Hz","response":"1ms","hdr":"No","ports":"HDMI x2, DP"}),
            ("ASUS VZ24EHE 24 inch FHD IPS 75Hz", 2490000, 2990000, {"panel":"24 inch IPS","resolution":"1920x1080 FHD","refresh":"75Hz","response":"1ms","hdr":"No","ports":"HDMI, VGA"}),
        ],
        "colors": [["Đen"],["Đen"]],
        "tags_pool": ["gaming","ProArt","ROG","OLED","Mini LED","chuyên nghiệp","240Hz"]
    },
    "BenQ": {
        "models": [
            ("BenQ MOBIUZ EX2710U 27 inch 4K IPS 144Hz", 14990000, 17990000, {"panel":"27 inch IPS","resolution":"3840x2160 4K","refresh":"144Hz","response":"1ms","hdr":"HDR600","ports":"HDMI 2.1 x2, DP 1.4, USB-C"}),
            ("BenQ PD2725U 27 inch 4K IPS Thunderbolt 3", 18990000, 21990000, {"panel":"27 inch IPS","resolution":"3840x2160 4K","refresh":"60Hz","response":"5ms","hdr":"HDR400","ports":"HDMI, DP, Thunderbolt 3, USB-C"}),
            ("BenQ GW2780 27 inch FHD IPS", 3990000, 4690000, {"panel":"27 inch IPS","resolution":"1920x1080 FHD","refresh":"60Hz","response":"5ms","hdr":"No","ports":"HDMI, DP, VGA"}),
        ],
        "colors": [["Đen"],["Đen","Xám"]],
        "tags_pool": ["gaming","chuyên nghiệp","4K","Thunderbolt","màu chuẩn","eye-care"]
    },
}

SMARTWATCH_BRANDS = {
    "Apple": {
        "models": [
            ("Apple Watch Ultra 2 49mm GPS+Cellular", 21990000, 23990000, {"screen":"1.93 inch LTPO OLED","chip":"Apple S9 SiP","battery":"36 giờ","water":"100m","os":"watchOS 10","sensors":"ECG, SpO2, nhiệt độ"}),
            ("Apple Watch Series 10 46mm GPS", 11490000, 12990000, {"screen":"1.96 inch LTPO OLED","chip":"Apple S10 SiP","battery":"18 giờ","water":"50m","os":"watchOS 11","sensors":"ECG, SpO2"}),
            ("Apple Watch Series 10 42mm GPS", 10490000, 11490000, {"screen":"1.74 inch LTPO OLED","chip":"Apple S10 SiP","battery":"18 giờ","water":"50m","os":"watchOS 11","sensors":"ECG, SpO2"}),
            ("Apple Watch SE 2 44mm GPS", 6490000, 7490000, {"screen":"1.78 inch LTPO OLED","chip":"Apple S8 SiP","battery":"18 giờ","water":"50m","os":"watchOS 10","sensors":"nhịp tim, gia tốc"}),
        ],
        "colors": [["Titan Tự Nhiên","Titan Đen","Titan Cam"],["Bạc","Đen Nửa Đêm","Vàng Sao","Hồng"]],
        "tags_pool": ["cao cấp","thể thao","sức khỏe","ECG","GPS","chống nước"]
    },
    "Samsung": {
        "models": [
            ("Samsung Galaxy Watch Ultra 47mm", 14990000, 16990000, {"screen":"1.47 inch Super AMOLED","chip":"Exynos W1000","battery":"60 giờ","water":"100m","os":"Wear OS 5","sensors":"BIA, ECG, SpO2, nhiệt độ"}),
            ("Samsung Galaxy Watch7 44mm", 7490000, 8990000, {"screen":"1.47 inch Super AMOLED","chip":"Exynos W1000","battery":"40 giờ","water":"50m","os":"Wear OS 5","sensors":"BIA, ECG, SpO2"}),
            ("Samsung Galaxy Watch FE 40mm", 4990000, 5990000, {"screen":"1.2 inch Super AMOLED","chip":"Exynos W920","battery":"30 giờ","water":"50m","os":"Wear OS 4","sensors":"nhịp tim, SpO2"}),
            ("Samsung Galaxy Fit3", 1290000, 1490000, {"screen":"1.6 inch AMOLED","chip":"–","battery":"13 ngày","water":"50m","os":"–","sensors":"nhịp tim, SpO2, giấc ngủ"}),
        ],
        "colors": [["Titan Bạc","Titan Xám","Titan Trắng"],["Đen","Xanh","Kem"]],
        "tags_pool": ["Galaxy AI","sức khỏe","thể thao","BIA","ECG","Wear OS"]
    },
    "Garmin": {
        "models": [
            ("Garmin Fenix 8 47mm Solar", 22990000, 25990000, {"screen":"1.4 inch MIP","chip":"–","battery":"48 ngày Solar","water":"100m","os":"Garmin OS","sensors":"nhịp tim, SpO2, nhiệt độ, la bàn, bản đồ"}),
            ("Garmin Forerunner 965", 13490000, 15490000, {"screen":"1.4 inch AMOLED","chip":"–","battery":"23 ngày","water":"50m","os":"Garmin OS","sensors":"nhịp tim, SpO2, bản đồ, GPS đa băng"}),
            ("Garmin Venu 3 45mm", 11990000, 13490000, {"screen":"1.4 inch AMOLED","chip":"–","battery":"14 ngày","water":"50m","os":"Garmin OS","sensors":"nhịp tim, SpO2, giấc ngủ, stress"}),
            ("Garmin Instinct 2X Solar", 8990000, 10490000, {"screen":"1.1 inch MIP","chip":"–","battery":"Không giới hạn Solar","water":"100m","os":"Garmin OS","sensors":"nhịp tim, SpO2, la bàn, GPS"}),
            ("Garmin Lily 2 Sport", 4990000, 5990000, {"screen":"1 inch LCD","chip":"–","battery":"5 ngày","water":"50m","os":"Garmin OS","sensors":"nhịp tim, SpO2, stress, giấc ngủ"}),
        ],
        "colors": [["Đen","Xám"],["Trắng","Hồng","Đen","Xanh"]],
        "tags_pool": ["outdoor","thể thao chuyên nghiệp","GPS","solar","bản đồ","bền bỉ"]
    },
    "Xiaomi": {
        "models": [
            ("Xiaomi Watch S3 46mm", 3490000, 4290000, {"screen":"1.43 inch AMOLED","chip":"–","battery":"15 ngày","water":"50m","os":"Xiaomi HyperOS","sensors":"nhịp tim, SpO2, GPS"}),
            ("Xiaomi Smart Band 9", 990000, 1190000, {"screen":"1.62 inch AMOLED","chip":"–","battery":"21 ngày","water":"50m","os":"–","sensors":"nhịp tim, SpO2, giấc ngủ"}),
        ],
        "colors": [["Đen","Bạc","Xám"],["Đen","Xanh","Hồng","Cam"]],
        "tags_pool": ["giá tốt","pin trâu","AMOLED","nhỏ gọn"]
    },
}

CAMERA_BRANDS = {
    "Sony": {
        "models": [
            ("Sony Alpha A7 IV Body", 42990000, 48990000, {"sensor":"33MP Full-Frame CMOS","iso":"50-204800","video":"4K 60fps","af":"759 điểm AI AF","evf":"3.69M dot OLED","weight":"573g"}),
            ("Sony Alpha A7C II Body", 38990000, 43990000, {"sensor":"33MP Full-Frame CMOS","iso":"50-204800","video":"4K 60fps","af":"759 điểm AI AF","evf":"2.36M dot OLED","weight":"429g"}),
            ("Sony Alpha A6700 Body", 29990000, 33990000, {"sensor":"26MP APS-C CMOS","iso":"50-102400","video":"4K 120fps","af":"759 điểm AI AF","evf":"2.36M dot OLED","weight":"409g"}),
            ("Sony ZV-E10 II Body", 18990000, 21990000, {"sensor":"26MP APS-C CMOS","iso":"100-51200","video":"4K 60fps","af":"759 điểm AI AF","evf":"–","weight":"292g"}),
            ("Sony ZV-1 II", 17990000, 19990000, {"sensor":"20.1MP 1 inch CMOS","iso":"80-12800","video":"4K 30fps","af":"315 điểm","evf":"–","weight":"292g"}),
            ("Sony Alpha A7R V Body", 72990000, 79990000, {"sensor":"61MP Full-Frame CMOS","iso":"50-102400","video":"8K 24fps","af":"693 điểm AI AF","evf":"9.44M dot OLED","weight":"638g"}),
        ],
        "colors": [["Đen"],["Đen","Bạc"]],
        "tags_pool": ["mirrorless","full-frame","4K","AI AF","chuyên nghiệp","vlog"]
    },
    "Canon": {
        "models": [
            ("Canon EOS R6 Mark III Body", 59990000, 65990000, {"sensor":"24.2MP Full-Frame CMOS","iso":"50-204800","video":"6K 60fps","af":"1053 điểm Dual Pixel","evf":"3.69M dot OLED","weight":"600g"}),
            ("Canon EOS R8 Body", 32990000, 37990000, {"sensor":"24.2MP Full-Frame CMOS","iso":"50-102400","video":"4K 60fps","af":"1053 điểm Dual Pixel","evf":"2.36M dot OLED","weight":"414g"}),
            ("Canon EOS R50 Body", 16990000, 19990000, {"sensor":"24.2MP APS-C CMOS","iso":"100-51200","video":"4K 30fps","af":"651 điểm Dual Pixel","evf":"2.36M dot OLED","weight":"328g"}),
            ("Canon EOS R100 Body", 10990000, 12990000, {"sensor":"24.1MP APS-C CMOS","iso":"100-12800","video":"4K 30fps","af":"3975 điểm Dual Pixel","evf":"2.36M dot","weight":"309g"}),
            ("Canon PowerShot V10", 8990000, 10490000, {"sensor":"13.2MP 1 inch CMOS","iso":"125-12800","video":"4K 30fps","af":"–","evf":"–","weight":"211g"}),
        ],
        "colors": [["Đen"],["Đen","Trắng"]],
        "tags_pool": ["mirrorless","full-frame","4K","Dual Pixel AF","chuyên nghiệp","vlog"]
    },
    "Fujifilm": {
        "models": [
            ("Fujifilm X-T5 Body", 37990000, 42990000, {"sensor":"40MP APS-C X-Trans CMOS 5 HR","iso":"64-51200","video":"6.2K 30fps","af":"425 điểm","evf":"3.69M dot OLED","weight":"476g"}),
            ("Fujifilm X-S20 Body", 28990000, 32990000, {"sensor":"26.1MP APS-C CMOS","iso":"80-51200","video":"6.2K 30fps","af":"425 điểm AI AF","evf":"2.36M dot OLED","weight":"383g"}),
            ("Fujifilm X100VI", 38990000, 43990000, {"sensor":"40.2MP APS-C X-Trans CMOS 5 HR","iso":"64-51200","video":"6.2K 30fps","af":"425 điểm AI AF","evf":"3.69M dot hybrid","weight":"521g"}),
            ("Fujifilm Instax Mini 12", 1790000, 2190000, {"sensor":"–","iso":"–","video":"–","af":"Auto","evf":"Viewfinder quang học","weight":"306g"}),
        ],
        "colors": [["Đen","Bạc"],["Bạc","Đen"],["Xanh Pastel","Hồng","Trắng","Tím","Xanh Lá"]],
        "tags_pool": ["retro","film simulation","APS-C","chụp ảnh","vlog","Instax"]
    },
    "Nikon": {
        "models": [
            ("Nikon Z8 Body", 79990000, 86990000, {"sensor":"45.7MP Full-Frame CMOS","iso":"32-102400","video":"8K 30fps","af":"493 điểm 3D tracking","evf":"3.69M dot OLED","weight":"820g"}),
            ("Nikon Z6 III Body", 48990000, 53990000, {"sensor":"24.5MP Full-Frame CMOS","iso":"50-204800","video":"6K 60fps","af":"299 điểm 3D tracking","evf":"5.76M dot OLED","weight":"600g"}),
            ("Nikon Z50 II Body", 22990000, 25990000, {"sensor":"20.9MP APS-C CMOS","iso":"100-51200","video":"4K 30fps","af":"209 điểm","evf":"2.36M dot OLED","weight":"395g"}),
            ("Nikon Zf Body", 42990000, 47990000, {"sensor":"24.5MP Full-Frame CMOS","iso":"64-64000","video":"4K 30fps","af":"299 điểm","evf":"3.69M dot OLED","weight":"630g"}),
        ],
        "colors": [["Đen"],["Đen","Bạc Retro"]],
        "tags_pool": ["mirrorless","full-frame","8K","3D tracking","chuyên nghiệp","retro"]
    },
    "GoPro": {
        "models": [
            ("GoPro HERO13 Black", 10990000, 12490000, {"sensor":"27MP","iso":"100-6400","video":"5.3K 60fps","af":"–","evf":"–","weight":"154g"}),
            ("GoPro HERO13 Black Creator Edition", 14990000, 16990000, {"sensor":"27MP","iso":"100-6400","video":"5.3K 60fps","af":"–","evf":"–","weight":"154g + phụ kiện"}),
        ],
        "colors": [["Đen"]],
        "tags_pool": ["action cam","chống nước","5.3K","nhỏ gọn","vlog"]
    },
    "DJI": {
        "models": [
            ("DJI Osmo Action 5 Pro", 9490000, 10990000, {"sensor":"40MP","iso":"100-12800","video":"4K 120fps","af":"–","evf":"–","weight":"145g"}),
            ("DJI Pocket 3", 12990000, 14990000, {"sensor":"1 inch CMOS","iso":"100-6400","video":"4K 120fps","af":"–","evf":"2 inch OLED","weight":"179g"}),
            ("DJI Mini 4 Pro Fly More Combo", 22990000, 25990000, {"sensor":"48MP 1/1.3 inch CMOS","iso":"100-6400","video":"4K 100fps","af":"APAS 5.0","evf":"–","weight":"249g (drone)"}),
            ("DJI Air 3 Fly More Combo", 28990000, 32990000, {"sensor":"48MP 1/1.3 inch CMOS x2","iso":"100-6400","video":"4K 100fps","af":"APAS 5.0","evf":"–","weight":"720g (drone)"}),
        ],
        "colors": [["Đen"],["Xám"]],
        "tags_pool": ["action cam","drone","gimbal","4K","chuyên nghiệp","flycam"]
    },
}

STORAGE_BRANDS = {
    "Samsung": {
        "models": [
            ("Samsung SSD 990 PRO 1TB NVMe PCIe 4.0", 3290000, 3890000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"7450 MB/s","write":"6900 MB/s","capacity":"1TB","endurance":"600 TBW"}),
            ("Samsung SSD 990 PRO 2TB NVMe PCIe 4.0", 5490000, 6490000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"7450 MB/s","write":"6900 MB/s","capacity":"2TB","endurance":"1200 TBW"}),
            ("Samsung SSD 990 EVO Plus 1TB NVMe PCIe 5.0", 2990000, 3490000, {"type":"NVMe M.2 2280","interface":"PCIe 5.0 x4","read":"7250 MB/s","write":"6300 MB/s","capacity":"1TB","endurance":"600 TBW"}),
            ("Samsung SSD 870 EVO 1TB SATA", 2290000, 2790000, {"type":"2.5 inch SATA","interface":"SATA III","read":"560 MB/s","write":"530 MB/s","capacity":"1TB","endurance":"600 TBW"}),
            ("Samsung T7 Shield 1TB Portable SSD", 2490000, 2990000, {"type":"Portable USB 3.2","interface":"USB 3.2 Gen 2","read":"1050 MB/s","write":"1000 MB/s","capacity":"1TB","endurance":"–"}),
            ("Samsung T7 Shield 2TB Portable SSD", 3990000, 4690000, {"type":"Portable USB 3.2","interface":"USB 3.2 Gen 2","read":"1050 MB/s","write":"1000 MB/s","capacity":"2TB","endurance":"–"}),
            ("Samsung PRO Plus microSD 256GB A2 V30", 690000, 890000, {"type":"microSD","interface":"UHS-I U3","read":"180 MB/s","write":"130 MB/s","capacity":"256GB","endurance":"–"}),
        ],
        "colors": [["Đen"],["Đen","Xanh"]],
        "tags_pool": ["SSD","NVMe","PCIe 5.0","tốc độ cao","portable","bền bỉ"]
    },
    "Western Digital": {
        "models": [
            ("WD Black SN850X 1TB NVMe PCIe 4.0", 2890000, 3490000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"7300 MB/s","write":"6300 MB/s","capacity":"1TB","endurance":"600 TBW"}),
            ("WD Black SN850X 2TB NVMe PCIe 4.0", 4990000, 5990000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"7300 MB/s","write":"6600 MB/s","capacity":"2TB","endurance":"1200 TBW"}),
            ("WD Blue SN580 1TB NVMe PCIe 4.0", 1790000, 2290000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"4150 MB/s","write":"4150 MB/s","capacity":"1TB","endurance":"600 TBW"}),
            ("WD My Passport 2TB HDD", 1690000, 2090000, {"type":"Portable HDD","interface":"USB 3.0","read":"–","write":"–","capacity":"2TB","endurance":"–"}),
            ("WD My Passport 4TB HDD", 2790000, 3290000, {"type":"Portable HDD","interface":"USB 3.0","read":"–","write":"–","capacity":"4TB","endurance":"–"}),
            ("SanDisk Extreme Pro 1TB Portable SSD", 2290000, 2790000, {"type":"Portable USB 3.2","interface":"USB 3.2 Gen 2x2","read":"2000 MB/s","write":"2000 MB/s","capacity":"1TB","endurance":"–"}),
        ],
        "colors": [["Đen"],["Đen","Xanh","Đỏ"]],
        "tags_pool": ["SSD","NVMe","HDD","portable","gaming","tốc độ cao"]
    },
    "Seagate": {
        "models": [
            ("Seagate FireCuda 530 1TB NVMe PCIe 4.0", 2990000, 3590000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"7300 MB/s","write":"6000 MB/s","capacity":"1TB","endurance":"1275 TBW"}),
            ("Seagate One Touch 2TB HDD", 1590000, 1990000, {"type":"Portable HDD","interface":"USB 3.0","read":"–","write":"–","capacity":"2TB","endurance":"–"}),
            ("Seagate One Touch 4TB HDD", 2490000, 2990000, {"type":"Portable HDD","interface":"USB 3.0","read":"–","write":"–","capacity":"4TB","endurance":"–"}),
            ("Seagate Expansion 1TB HDD", 990000, 1290000, {"type":"Portable HDD","interface":"USB 3.0","read":"–","write":"–","capacity":"1TB","endurance":"–"}),
        ],
        "colors": [["Đen"],["Đen","Xanh","Bạc"]],
        "tags_pool": ["HDD","NVMe","portable","gaming","lưu trữ lớn"]
    },
    "Kingston": {
        "models": [
            ("Kingston FURY Renegade 1TB NVMe PCIe 4.0 Heatsink", 2490000, 2990000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"7300 MB/s","write":"7000 MB/s","capacity":"1TB","endurance":"–"}),
            ("Kingston NV2 1TB NVMe PCIe 4.0", 1290000, 1590000, {"type":"NVMe M.2 2280","interface":"PCIe 4.0 x4","read":"3500 MB/s","write":"2100 MB/s","capacity":"1TB","endurance":"–"}),
            ("Kingston XS1000 1TB Portable SSD", 1690000, 2090000, {"type":"Portable USB 3.2","interface":"USB 3.2 Gen 2","read":"1050 MB/s","write":"1000 MB/s","capacity":"1TB","endurance":"–"}),
            ("Kingston Canvas Go Plus microSD 512GB", 890000, 1090000, {"type":"microSD","interface":"UHS-I U3","read":"170 MB/s","write":"90 MB/s","capacity":"512GB","endurance":"–"}),
        ],
        "colors": [["Đen"],["Đen","Xanh"]],
        "tags_pool": ["SSD","NVMe","giá tốt","gaming","portable"]
    },
}

ACCESSORY_TYPES = {
    "Tai nghe": {
        "models": [
            ("Apple AirPods Pro 2 USB-C","Apple",5990000,6490000,{"driver":"–","anc":"ANC chủ động","bluetooth":"5.3","battery":"6h (30h với hộp)","water":"IPX4","type":"True Wireless"}),
            ("Apple AirPods 4 ANC","Apple",4990000,5490000,{"driver":"–","anc":"ANC chủ động","bluetooth":"5.3","battery":"5h (30h với hộp)","water":"IP54","type":"True Wireless"}),
            ("Apple AirPods Max USB-C","Apple",13990000,15490000,{"driver":"40mm","anc":"ANC chủ động","bluetooth":"5.3","battery":"20h","water":"–","type":"Over-Ear"}),
            ("Samsung Galaxy Buds3 Pro","Samsung",4990000,5490000,{"driver":"10.5mm + 6.1mm","anc":"ANC chủ động 360","bluetooth":"5.4","battery":"6h (26h với hộp)","water":"IP57","type":"True Wireless"}),
            ("Samsung Galaxy Buds3","Samsung",3290000,3790000,{"driver":"11mm","anc":"ANC chủ động","bluetooth":"5.4","battery":"5h (24h với hộp)","water":"IP57","type":"True Wireless"}),
            ("Sony WH-1000XM5","Sony",7490000,8490000,{"driver":"30mm","anc":"ANC chủ động","bluetooth":"5.3","battery":"30h","water":"–","type":"Over-Ear"}),
            ("Sony WF-1000XM5","Sony",5990000,6490000,{"driver":"8.4mm","anc":"ANC chủ động","bluetooth":"5.3","battery":"8h (24h với hộp)","water":"IPX4","type":"True Wireless"}),
            ("Sony WH-CH720N","Sony",2490000,2990000,{"driver":"30mm","anc":"ANC chủ động","bluetooth":"5.2","battery":"35h","water":"–","type":"Over-Ear"}),
            ("JBL Tune 770NC","JBL",1990000,2490000,{"driver":"40mm","anc":"ANC chủ động","bluetooth":"5.3","battery":"44h","water":"–","type":"Over-Ear"}),
            ("JBL Tune Beam 2","JBL",1790000,2190000,{"driver":"10mm","anc":"ANC chủ động","bluetooth":"5.3","battery":"10h (40h với hộp)","water":"IP54","type":"True Wireless"}),
            ("JBL Live Pro 2","JBL",2490000,2990000,{"driver":"11mm","anc":"ANC chủ động","bluetooth":"5.3","battery":"10h (40h với hộp)","water":"IPX5","type":"True Wireless"}),
            ("Marshall Major V","Marshall",3290000,3690000,{"driver":"40mm","anc":"–","bluetooth":"5.3","battery":"100h+","water":"–","type":"On-Ear"}),
            ("Marshall Minor IV","Marshall",2790000,3190000,{"driver":"12mm","anc":"–","bluetooth":"5.3","battery":"7h (30h với hộp)","water":"IPX4","type":"True Wireless"}),
            ("Bose QuietComfort Ultra Headphones","Bose",8990000,9990000,{"driver":"–","anc":"ANC chủ động","bluetooth":"5.3","battery":"24h","water":"–","type":"Over-Ear"}),
            ("Bose QuietComfort Ultra Earbuds","Bose",6490000,7490000,{"driver":"–","anc":"ANC chủ động","bluetooth":"5.3","battery":"6h (24h với hộp)","water":"IPX4","type":"True Wireless"}),
            ("Edifier W820NB Plus","Edifier",1190000,1490000,{"driver":"40mm","anc":"ANC chủ động","bluetooth":"5.3","battery":"49h","water":"–","type":"Over-Ear"}),
            ("Logitech Zone Vibe 125","Logitech",1790000,2190000,{"driver":"40mm","anc":"–","bluetooth":"5.3","battery":"18h","water":"–","type":"Over-Ear"}),
        ],
        "colors_pool": [["Đen","Trắng"],["Đen","Trắng","Xanh"],["Đen","Kem","Bạc"],["Đen"]],
        "tags_pool": ["ANC","bluetooth","true wireless","over-ear","chống ồn","pin trâu","âm thanh hay"]
    },
    "Bàn phím": {
        "models": [
            ("Logitech MX Keys S Wireless","Logitech",2690000,3190000,{"type":"membrane","connect":"Bluetooth + USB Receiver","switch":"–","backlight":"LED trắng","battery":"10 ngày","layout":"Full-size"}),
            ("Logitech MX Mechanical Mini","Logitech",3490000,3990000,{"type":"mechanical","connect":"Bluetooth + USB Receiver","switch":"Tactile Quiet","backlight":"LED trắng","battery":"15 ngày","layout":"75%"}),
            ("Logitech K380 Multi-Device","Logitech",790000,990000,{"type":"membrane","connect":"Bluetooth","switch":"–","backlight":"–","battery":"2 năm","layout":"Compact"}),
            ("Keychron K2 Pro QMK","Keychron",1890000,2290000,{"type":"mechanical","connect":"Bluetooth + USB-C","switch":"Gateron Brown/Red/Blue","backlight":"RGB","battery":"4000mAh","layout":"75%"}),
            ("Keychron Q1 Max","Keychron",4490000,5190000,{"type":"mechanical","connect":"Bluetooth + 2.4GHz + USB-C","switch":"Gateron Jupiter Brown","backlight":"RGB","battery":"4000mAh","layout":"75%"}),
            ("Keychron V6 Max","Keychron",2490000,2990000,{"type":"mechanical","connect":"Bluetooth + 2.4GHz + USB-C","switch":"Gateron Jupiter Brown","backlight":"RGB","battery":"4000mAh","layout":"Full-size"}),
            ("Razer BlackWidow V4 75%","Razer",4490000,5190000,{"type":"mechanical","connect":"USB-C + Bluetooth","switch":"Razer Orange","backlight":"RGB","battery":"–","layout":"75%"}),
            ("Razer Huntsman V3 Pro TKL","Razer",5990000,6690000,{"type":"analog optical","connect":"USB-C","switch":"Razer Analog Optical Gen 2","backlight":"RGB","battery":"–","layout":"TKL"}),
            ("Corsair K70 RGB PRO","Corsair",3290000,3890000,{"type":"mechanical","connect":"USB","switch":"Cherry MX Red","backlight":"RGB","battery":"–","layout":"Full-size"}),
            ("Royal Kludge RK84 Pro","Royal Kludge",1290000,1590000,{"type":"mechanical","connect":"Bluetooth + 2.4GHz + USB-C","switch":"RK Brown/Red/Blue","backlight":"RGB","battery":"3750mAh","layout":"75%"}),
            ("Akko 3068B Plus","Akko",1490000,1790000,{"type":"mechanical","connect":"Bluetooth + USB-C","switch":"Akko CS","backlight":"RGB","battery":"3000mAh","layout":"65%"}),
        ],
        "colors_pool": [["Đen","Xám"],["Đen","Trắng"],["Đen","Hồng","Xanh"]],
        "tags_pool": ["mechanical","wireless","bluetooth","RGB","gaming","văn phòng","hot-swap"]
    },
    "Chuột": {
        "models": [
            ("Logitech MX Master 3S","Logitech",2290000,2690000,{"sensor":"8000 DPI","connect":"Bluetooth + USB Receiver","battery":"70 ngày","weight":"141g","buttons":"7","type":"Ergonomic"}),
            ("Logitech MX Anywhere 3S","Logitech",1690000,1990000,{"sensor":"8000 DPI","connect":"Bluetooth + USB Receiver","battery":"70 ngày","weight":"99g","buttons":"6","type":"Compact"}),
            ("Logitech G Pro X Superlight 2","Logitech",2990000,3490000,{"sensor":"HERO 2 32000 DPI","connect":"2.4GHz Wireless","battery":"95h","weight":"60g","buttons":"5","type":"Gaming"}),
            ("Logitech G502 X Plus","Logitech",3290000,3790000,{"sensor":"HERO 25600 DPI","connect":"2.4GHz + Bluetooth","battery":"130h","weight":"106g","buttons":"13","type":"Gaming"}),
            ("Razer DeathAdder V3 Pro","Razer",3490000,3990000,{"sensor":"Focus Pro 30000 DPI","connect":"2.4GHz + USB-C","battery":"90h","weight":"63g","buttons":"5","type":"Gaming"}),
            ("Razer Viper V3 Pro","Razer",4490000,4990000,{"sensor":"Focus Pro 36000 DPI","connect":"2.4GHz + USB-C","battery":"95h","weight":"54g","buttons":"5","type":"Gaming"}),
            ("Razer Basilisk V3 Pro","Razer",3290000,3790000,{"sensor":"Focus Pro 30000 DPI","connect":"2.4GHz + Bluetooth + USB-C","battery":"90h","weight":"112g","buttons":"11","type":"Gaming"}),
            ("Apple Magic Mouse USB-C","Apple",2490000,2790000,{"sensor":"–","connect":"Bluetooth","battery":"1 tháng","weight":"99g","buttons":"Multitouch","type":"Multitouch"}),
            ("SteelSeries Aerox 5 Wireless","SteelSeries",2190000,2690000,{"sensor":"18000 DPI","connect":"2.4GHz + Bluetooth + USB-C","battery":"180h","weight":"74g","buttons":"9","type":"Gaming"}),
            ("Corsair Dark Core RGB Pro SE","Corsair",2490000,2990000,{"sensor":"18000 DPI","connect":"2.4GHz + Bluetooth + USB-C","battery":"50h","weight":"133g","buttons":"8","type":"Gaming"}),
        ],
        "colors_pool": [["Đen","Trắng"],["Đen","Hồng"],["Đen"]],
        "tags_pool": ["wireless","gaming","ergonomic","siêu nhẹ","DPI cao","bluetooth"]
    },
    "Sạc & Cáp": {
        "models": [
            ("Anker 737 GaNPrime 120W 3-port","Anker",1490000,1790000,{"type":"Củ sạc","output":"120W (USB-C x2, USB-A x1)","tech":"GaN","protocol":"PD 3.1, QC 5.0","cable":"–","weight":"187g"}),
            ("Anker 735 GaNPrime 65W 3-port","Anker",890000,1090000,{"type":"Củ sạc","output":"65W (USB-C x2, USB-A x1)","tech":"GaN","protocol":"PD 3.0, QC 4+","cable":"–","weight":"112g"}),
            ("Anker 313 USB-C to Lightning 1.8m","Anker",290000,390000,{"type":"Cáp","output":"–","tech":"MFi","protocol":"–","cable":"USB-C to Lightning 1.8m","weight":"30g"}),
            ("Apple 35W Dual USB-C Compact","Apple",1190000,1390000,{"type":"Củ sạc","output":"35W (USB-C x2)","tech":"–","protocol":"PD","cable":"–","weight":"105g"}),
            ("Apple 20W USB-C Power Adapter","Apple",490000,590000,{"type":"Củ sạc","output":"20W (USB-C x1)","tech":"–","protocol":"PD","cable":"–","weight":"60g"}),
            ("Samsung 45W Super Fast Charger","Samsung",590000,790000,{"type":"Củ sạc","output":"45W (USB-C x1)","tech":"–","protocol":"PD 3.0, PPS","cable":"–","weight":"85g"}),
            ("Baseus 67W GaN 3-port","Baseus",690000,890000,{"type":"Củ sạc","output":"67W (USB-C x2, USB-A x1)","tech":"GaN","protocol":"PD 3.0, QC 4+","cable":"–","weight":"130g"}),
            ("Ugreen 100W USB-C Cable 1.5m","Ugreen",190000,290000,{"type":"Cáp","output":"–","tech":"E-Marker","protocol":"PD 3.0 100W","cable":"USB-C to USB-C 1.5m","weight":"40g"}),
            ("Anker 622 MagGo Wireless Power Bank 5000mAh","Anker",790000,990000,{"type":"Pin dự phòng","output":"7.5W MagSafe","tech":"MagSafe","protocol":"Qi","cable":"–","weight":"150g"}),
            ("Anker PowerCore 26800mAh PD 87W","Anker",1290000,1590000,{"type":"Pin dự phòng","output":"87W USB-C PD","tech":"–","protocol":"PD 3.0","cable":"–","weight":"580g"}),
            ("Xiaomi 20000mAh 50W Power Bank","Xiaomi",490000,690000,{"type":"Pin dự phòng","output":"50W USB-C","tech":"–","protocol":"PD 3.0, QC 3.0","cable":"–","weight":"400g"}),
            ("Samsung 10000mAh 25W Wireless Power Bank","Samsung",790000,990000,{"type":"Pin dự phòng","output":"25W + 7.5W Qi","tech":"–","protocol":"PD, Qi","cable":"–","weight":"230g"}),
            ("Apple MagSafe Charger","Apple",990000,1190000,{"type":"Sạc không dây","output":"15W MagSafe","tech":"MagSafe","protocol":"Qi2","cable":"–","weight":"–"}),
            ("Belkin BoostCharge Pro 3-in-1 MagSafe","Belkin",3490000,3990000,{"type":"Sạc không dây","output":"15W MagSafe + 5W AirPods + 5W Watch","tech":"MagSafe","protocol":"Qi2","cable":"–","weight":"–"}),
        ],
        "colors_pool": [["Đen","Trắng"],["Đen"],["Trắng","Đen","Xanh"]],
        "tags_pool": ["sạc nhanh","GaN","MagSafe","pin dự phòng","USB-C","PD","wireless charging"]
    },
    "Loa": {
        "models": [
            ("JBL Flip 6","JBL",2490000,2990000,{"driver":"–","power":"30W","battery":"12h","water":"IP67","connect":"Bluetooth 5.1","type":"Portable"}),
            ("JBL Charge 5","JBL",3490000,3990000,{"driver":"–","power":"40W","battery":"20h","water":"IP67","connect":"Bluetooth 5.1","type":"Portable"}),
            ("JBL Xtreme 4","JBL",6490000,7490000,{"driver":"–","power":"100W","battery":"24h","water":"IP67","connect":"Bluetooth 5.3","type":"Portable"}),
            ("Marshall Emberton III","Marshall",3490000,3990000,{"driver":"–","power":"30W","battery":"32h","water":"IP67","connect":"Bluetooth 5.3","type":"Portable"}),
            ("Marshall Stanmore III","Marshall",8490000,9490000,{"driver":"–","power":"80W","battery":"–","water":"–","connect":"Bluetooth 5.2, WiFi","type":"Home Speaker"}),
            ("Bose SoundLink Flex 2","Bose",3490000,3990000,{"driver":"–","power":"–","battery":"12h","water":"IP67","connect":"Bluetooth 5.3","type":"Portable"}),
            ("Sony SRS-XB100","Sony",990000,1290000,{"driver":"46mm","power":"–","battery":"16h","water":"IP67","connect":"Bluetooth 5.3","type":"Portable"}),
            ("Sony SRS-XG300","Sony",5990000,6990000,{"driver":"–","power":"–","battery":"25h","water":"IP67","connect":"Bluetooth 5.2","type":"Portable"}),
            ("Harman Kardon Aura Studio 4","Harman Kardon",5490000,6490000,{"driver":"–","power":"130W","battery":"–","water":"–","connect":"Bluetooth 5.3, WiFi","type":"Home Speaker"}),
            ("Apple HomePod mini","Apple",2490000,2990000,{"driver":"–","power":"–","battery":"–","water":"–","connect":"WiFi, Bluetooth 5.0","type":"Smart Speaker"}),
        ],
        "colors_pool": [["Đen","Xanh","Đỏ","Hồng"],["Đen","Kem","Xám"],["Đen","Trắng"]],
        "tags_pool": ["bluetooth","chống nước","pin trâu","âm bass","portable","loa thông minh"]
    },
    "Bao da / Ốp lưng": {
        "models": [
            ("Apple iPhone 15 Pro Max Silicone Case MagSafe","Apple",1290000,1490000,{"material":"Silicone","compatibility":"iPhone 15 Pro Max","feature":"MagSafe","weight":"–","type":"Ốp lưng"}),
            ("Apple iPhone 16 Pro Clear Case MagSafe","Apple",1190000,1390000,{"material":"Polycarbonate + MagSafe","compatibility":"iPhone 16 Pro","feature":"MagSafe, trong suốt","weight":"–","type":"Ốp lưng"}),
            ("Samsung Galaxy S24 Ultra Silicone Case","Samsung",590000,790000,{"material":"Silicone","compatibility":"Galaxy S24 Ultra","feature":"–","weight":"–","type":"Ốp lưng"}),
            ("Spigen Ultra Hybrid iPhone 15 Pro","Spigen",490000,690000,{"material":"TPU + PC","compatibility":"iPhone 15 Pro","feature":"Trong suốt, chống sốc","weight":"–","type":"Ốp lưng"}),
            ("UAG Monarch Samsung Galaxy S24 Ultra","UAG",990000,1290000,{"material":"Polycarbonate + TPU","compatibility":"Galaxy S24 Ultra","feature":"5 lớp bảo vệ, MIL-STD-810G","weight":"–","type":"Ốp lưng"}),
            ("Ringke Fusion iPad Air M2","Ringke",490000,690000,{"material":"TPU + PC","compatibility":"iPad Air M2","feature":"Trong suốt, chống sốc","weight":"–","type":"Ốp lưng"}),
        ],
        "colors_pool": [["Đen","Trong suốt","Xanh","Đỏ","Hồng"],["Đen","Xanh Navy","Đỏ"]],
        "tags_pool": ["MagSafe","chống sốc","trong suốt","chính hãng","bảo vệ"]
    },
}

# Category mapping for the expand
CATEGORY_SOURCES = {
    "Điện thoại": PHONE_BRANDS,
    "Laptop": LAPTOP_BRANDS,
    "Máy tính bảng": TABLET_BRANDS,
    "Màn hình": MONITOR_BRANDS,
    "Đồng hồ thông minh": SMARTWATCH_BRANDS,
    "Máy ảnh": CAMERA_BRANDS,
    "Lưu trữ": STORAGE_BRANDS,
}

# Target distribution for 1000 products
TARGET_COUNT = {
    "Điện thoại": 150,
    "Laptop": 200,
    "Máy tính bảng": 65,
    "Màn hình": 100,
    "Đồng hồ thông minh": 80,
    "Máy ảnh": 100,
    "Lưu trữ": 90,
    "Phụ kiện": 215,
}

def gen_description(name, category, brand, specs):
    """Generate a realistic Vietnamese product description."""
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
    discount = max(0, min(40, round((1 - price/original_price) * 100)))
    rating = round(random.uniform(3.8, 4.9), 1)
    reviews = random.randint(50, 2000)
    stock = random.randint(5, 200)
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
new_products = list(existing)  # Start with existing
next_id = max_id + 1

# Track existing product names to avoid duplicates
existing_names = {p['name'] for p in existing}

def add_product_if_new(name, category, brand, price, orig_price, specs, colors, tags):
    global next_id
    if name in existing_names:
        return
    existing_names.add(name)
    p = create_product(next_id, name, category, brand, price, orig_price, specs, colors, tags)
    new_products.append(p)
    next_id += 1

# ── Generate from brand catalogs ──────────────────────────────
for category, brands_data in CATEGORY_SOURCES.items():
    for brand, data in brands_data.items():
        for model_tuple in data["models"]:
            name = model_tuple[0]
            price = model_tuple[1]
            orig_price = model_tuple[2]
            specs = model_tuple[3]
            colors = random.choice(data["colors"])
            tags = data["tags_pool"]
            add_product_if_new(name, category, brand, price, orig_price, specs, colors, tags)
            
            # Create price variants (different storage/config)
            if category in ["Điện thoại", "Laptop"] and random.random() < 0.4:
                variant_name = name.replace("256GB", "512GB").replace("128GB", "256GB").replace("512GB", "1TB")
                if variant_name != name:
                    variant_price = int(price * random.uniform(1.15, 1.35))
                    variant_orig = int(orig_price * random.uniform(1.15, 1.35))
                    variant_specs = dict(specs)
                    if "storage" in variant_specs:
                        variant_specs["storage"] = variant_specs["storage"].replace("256GB","512GB").replace("128GB","256GB").replace("512GB","1TB")
                    add_product_if_new(variant_name, category, brand, variant_price, variant_orig, variant_specs, colors, tags)

# ── Generate from accessory types ──────────────────────────────
for acc_type, data in ACCESSORY_TYPES.items():
    for model_tuple in data["models"]:
        name = model_tuple[0]
        brand = model_tuple[1]
        price = model_tuple[2]
        orig_price = model_tuple[3]
        specs = model_tuple[4]
        colors = random.choice(data["colors_pool"])
        tags = data["tags_pool"]
        add_product_if_new(name, "Phụ kiện", brand, price, orig_price, specs, colors, tags)

# ── Fill remaining slots with variations ──────────────────────
# Count current per category
def count_by_cat():
    cats = {}
    for p in new_products:
        cats[p['category']] = cats.get(p['category'], 0) + 1
    return cats

cat_counts = count_by_cat()
print(f"\nAfter initial generation: {len(new_products)} products")
for c, n in sorted(cat_counts.items()):
    target = TARGET_COUNT.get(c, 0)
    print(f"  {c}: {n}/{target}")

# Generate more products by creating variations of existing ones
def gen_price_variation(base_price, factor_range=(0.7, 1.3)):
    factor = random.uniform(factor_range[0], factor_range[1])
    return int(round(base_price * factor / 10000) * 10000)

# Additional products to fill gaps - create realistic variants
EXTRA_PHONE_NAMES = [
    ("Motorola Edge 50 Pro 256GB","Motorola"), ("Motorola Razr 50 Ultra 256GB","Motorola"),
    ("Honor Magic6 Pro 512GB","Honor"), ("Honor 200 Pro 256GB","Honor"), ("Honor X9b 256GB","Honor"),
    ("Tecno Phantom X2 Pro 256GB","Tecno"), ("Tecno Camon 30 Premier 512GB","Tecno"),
    ("Nokia G42 5G 128GB","Nokia"), ("Nokia X30 5G 256GB","Nokia"),
    ("Sony Xperia 1 VI 256GB","Sony"), ("Sony Xperia 5 V 256GB","Sony"),
    ("ASUS ROG Phone 8 Pro 512GB","ASUS"), ("ASUS Zenfone 11 Ultra 256GB","ASUS"),
    ("Huawei Nova 12 Ultra 256GB","Huawei"), ("Huawei Mate 60 Pro 256GB","Huawei"),
    ("Nubia Z60 Ultra 512GB","Nubia"), ("Nubia Red Magic 9 Pro 256GB","Nubia"),
]

EXTRA_LAPTOP_NAMES = [
    ("Gigabyte AORUS 15 RTX 4060 512GB","Gigabyte"), ("Gigabyte AERO 16 OLED RTX 4070 1TB","Gigabyte"),
    ("Razer Blade 16 RTX 4080 1TB","Razer"), ("Razer Blade 14 RTX 4070 1TB","Razer"),
    ("LG gram 17 Ultra 512GB","LG"), ("LG gram 16 2-in-1 512GB","LG"),
    ("Samsung Galaxy Book4 Ultra 1TB","Samsung"), ("Samsung Galaxy Book4 Pro 512GB","Samsung"),
    ("Huawei MateBook X Pro 2024 1TB","Huawei"), ("Huawei MateBook 14s 512GB","Huawei"),
    ("Microsoft Surface Laptop 6 512GB","Microsoft"), ("Microsoft Surface Pro 10 256GB","Microsoft"),
    ("Framework Laptop 16 DIY AMD 512GB","Framework"),
]

for name, brand in EXTRA_PHONE_NAMES:
    if len([p for p in new_products if p['category'] == 'Điện thoại']) >= TARGET_COUNT['Điện thoại']:
        break
    price = gen_price_variation(random.choice([5990000,8990000,12990000,18990000,24990000,29990000]))
    orig = int(price * random.uniform(1.1, 1.25))
    specs = {"screen":f"{random.uniform(6.1,6.9):.1f} inch AMOLED","chip":random.choice(["Snapdragon 8 Gen 3","Dimensity 9300","Snapdragon 7 Gen 3","Helio G99"]),"ram":random.choice(["6GB","8GB","12GB","16GB"]),"storage":random.choice(["128GB","256GB","512GB"]),"camera":random.choice(["50MP + 12MP","108MP + 8MP + 2MP","200MP + 50MP + 12MP"]),"battery":f"{random.randint(4000,6000)} mAh","os":random.choice(["Android 14","Android 15"])}
    add_product_if_new(name, "Điện thoại", brand, price, orig, specs, random.choice([["Đen","Trắng"],["Đen","Xanh","Bạc"]]), ["5G","AMOLED","sạc nhanh","camera AI"])

for name, brand in EXTRA_LAPTOP_NAMES:
    if len([p for p in new_products if p['category'] == 'Laptop']) >= TARGET_COUNT['Laptop']:
        break
    price = gen_price_variation(random.choice([15990000,22990000,32990000,42990000,52990000]))
    orig = int(price * random.uniform(1.08, 1.2))
    specs = {"screen":random.choice(["14 inch FHD","15.6 inch QHD","16 inch 4K OLED","14 inch 2.8K OLED"]),"chip":random.choice(["Intel Core Ultra 7 155H","AMD Ryzen 7 8845HS","Intel Core i7-14700H","Apple M3 Pro"]),"ram":random.choice(["8GB","16GB","32GB"]),"storage":random.choice(["256GB SSD","512GB SSD","1TB SSD"]),"gpu":random.choice(["Intel Arc Graphics","NVIDIA RTX 4060","NVIDIA RTX 4070","AMD Radeon 780M"]),"battery":random.choice(["50Wh","65Wh","75Wh","86Wh"]),"os":random.choice(["Windows 11","Windows 11 Pro","macOS Sequoia"])}
    add_product_if_new(name, "Laptop", brand, price, orig, specs, random.choice([["Bạc","Đen"],["Xám","Đen"]]), ["mỏng nhẹ","hiệu năng cao","OLED"])

# Additional monitors
EXTRA_MONITOR_NAMES = [
    ("ViewSonic VX2758 27 inch QHD IPS 165Hz","ViewSonic"),("ViewSonic VP2756-4K 27 inch 4K IPS","ViewSonic"),
    ("AOC 27G2SP 27 inch FHD IPS 165Hz","AOC"),("AOC U27P2C 27 inch 4K IPS USB-C","AOC"),
    ("Gigabyte M27U 27 inch 4K IPS 160Hz","Gigabyte"),("Gigabyte M32UC 32 inch 4K VA 160Hz Curved","Gigabyte"),
    ("MSI MAG 274UPF 27 inch 4K IPS 144Hz","MSI"),("MSI MPG 271QRX 27 inch QHD Rapid IPS 360Hz","MSI"),
    ("Philips 27M1N3200ZS 27 inch FHD IPS 165Hz","Philips"),("Philips 27E1N5800E 27 inch 4K IPS USB-C","Philips"),
]

for name, brand in EXTRA_MONITOR_NAMES:
    if len([p for p in new_products if p['category'] == 'Màn hình']) >= TARGET_COUNT['Màn hình']:
        break
    price = gen_price_variation(random.choice([3990000,5990000,8990000,12990000,18990000]))
    orig = int(price * random.uniform(1.1, 1.2))
    specs = {"panel":random.choice(["27 inch IPS","27 inch VA","32 inch IPS","27 inch OLED"]),"resolution":random.choice(["1920x1080","2560x1440","3840x2160"]),"refresh":random.choice(["75Hz","144Hz","165Hz","240Hz"]),"response":random.choice(["1ms","4ms","5ms"]),"hdr":random.choice(["No","HDR400","HDR600"]),"ports":"HDMI x2, DP 1.4"}
    add_product_if_new(name, "Màn hình", brand, price, orig, specs, ["Đen"], ["gaming","4K","IPS","USB-C"])

# Additional smartwatches
EXTRA_WATCH_NAMES = [
    ("Amazfit T-Rex Ultra","Amazfit"),("Amazfit GTR 4","Amazfit"),("Amazfit GTS 4","Amazfit"),("Amazfit Bip 5","Amazfit"),
    ("Huawei Watch GT 4 46mm","Huawei"),("Huawei Watch Fit 3","Huawei"),("Huawei Band 9","Huawei"),
    ("OPPO Watch 4 Pro","OPPO"),("OPPO Band 2","OPPO"),
    ("Fitbit Sense 2","Fitbit"),("Fitbit Charge 6","Fitbit"),("Fitbit Versa 4","Fitbit"),
    ("TicWatch Pro 5 Enduro","Mobvoi"),("TicWatch E3","Mobvoi"),
    ("Coros Pace 3","Coros"),("Coros Vertix 2S","Coros"),
]

for name, brand in EXTRA_WATCH_NAMES:
    if len([p for p in new_products if p['category'] == 'Đồng hồ thông minh']) >= TARGET_COUNT['Đồng hồ thông minh']:
        break
    price = gen_price_variation(random.choice([990000,2490000,4990000,7990000,12990000]))
    orig = int(price * random.uniform(1.1, 1.25))
    specs = {"screen":random.choice(["1.39 inch AMOLED","1.43 inch AMOLED","1.2 inch LCD","1.47 inch AMOLED"]),"chip":"–","battery":random.choice(["7 ngày","14 ngày","21 ngày","5 ngày"]),"water":"50m","os":random.choice(["Wear OS","Zepp OS","HarmonyOS","–"]),"sensors":"nhịp tim, SpO2, GPS"}
    add_product_if_new(name, "Đồng hồ thông minh", brand, price, orig, specs, random.choice([["Đen","Bạc"],["Đen","Hồng","Trắng"]]), ["sức khỏe","thể thao","GPS","pin trâu","AMOLED"])

# Additional cameras
EXTRA_CAMERA_NAMES = [
    ("Sony Alpha A9 III Body","Sony"),("Sony FX30 Cinema Body","Sony"),
    ("Canon EOS R5 Mark II Body","Canon"),("Canon EOS R7 Body","Canon"),
    ("Panasonic Lumix S5 IIX Body","Panasonic"),("Panasonic Lumix GH7 Body","Panasonic"),
    ("OM System OM-5 Body","OM System"),("OM System OM-1 Mark II Body","OM System"),
    ("Leica Q3","Leica"),("Leica M11 Body","Leica"),
    ("DJI Avata 2 Fly More Combo","DJI"),("DJI Mavic 3 Classic","DJI"),
    ("Insta360 X4","Insta360"),("Insta360 Ace Pro 2","Insta360"),
]

for name, brand in EXTRA_CAMERA_NAMES:
    if len([p for p in new_products if p['category'] == 'Máy ảnh']) >= TARGET_COUNT['Máy ảnh']:
        break
    price = gen_price_variation(random.choice([9990000,18990000,29990000,42990000,65990000]))
    orig = int(price * random.uniform(1.08, 1.2))
    specs = {"sensor":random.choice(["24MP Full-Frame","45MP Full-Frame","26MP APS-C","20MP MFT","48MP"]),"iso":random.choice(["100-51200","50-204800","100-25600"]),"video":random.choice(["4K 60fps","6K 30fps","8K 30fps","5.3K 60fps"]),"af":random.choice(["Phase Detect AF","Dual Pixel AF","AI AF","DFD AF"]),"evf":random.choice(["3.69M dot OLED","2.36M dot OLED","–"]),"weight":random.choice(["450g","600g","350g","720g","249g"])}
    add_product_if_new(name, "Máy ảnh", brand, price, orig, specs, random.choice([["Đen"],["Đen","Bạc"]]), ["mirrorless","4K","chuyên nghiệp","AI AF"])

# Additional storage
EXTRA_STORAGE_NAMES = [
    ("Crucial T700 1TB NVMe PCIe 5.0","Crucial"),("Crucial T500 1TB NVMe PCIe 4.0","Crucial"),("Crucial BX500 1TB SATA","Crucial"),
    ("SK hynix Platinum P41 1TB NVMe PCIe 4.0","SK hynix"),
    ("Corsair MP700 PRO 2TB NVMe PCIe 5.0","Corsair"),("Corsair MP600 1TB NVMe PCIe 4.0","Corsair"),
    ("Lexar NM790 1TB NVMe PCIe 4.0","Lexar"),("Lexar Professional NM800 PRO 1TB","Lexar"),
    ("ADATA Legend 970 1TB NVMe PCIe 5.0","ADATA"),("ADATA SE880 1TB Portable SSD","ADATA"),
    ("Sabrent Rocket 4 Plus-G 2TB NVMe","Sabrent"),
    ("PNY CS3040 1TB NVMe PCIe 4.0","PNY"),
]

for name, brand in EXTRA_STORAGE_NAMES:
    if len([p for p in new_products if p['category'] == 'Lưu trữ']) >= TARGET_COUNT['Lưu trữ']:
        break
    price = gen_price_variation(random.choice([1290000,1990000,2990000,4990000]))
    orig = int(price * random.uniform(1.1, 1.2))
    specs = {"type":"NVMe M.2 2280","interface":random.choice(["PCIe 4.0 x4","PCIe 5.0 x4"]),"read":random.choice(["5000 MB/s","7000 MB/s","7300 MB/s","12400 MB/s"]),"write":random.choice(["4000 MB/s","6000 MB/s","6500 MB/s","11800 MB/s"]),"capacity":random.choice(["1TB","2TB"]),"endurance":random.choice(["600 TBW","1200 TBW","–"])}
    add_product_if_new(name, "Lưu trữ", brand, price, orig, specs, ["Đen"], ["SSD","NVMe","tốc độ cao"])

# Additional accessories to fill 215 target
EXTRA_ACCESSORIES = [
    # Webcam
    ("Logitech Brio 4K Pro Webcam","Logitech","Phụ kiện",3290000,3890000,{"resolution":"4K 30fps / 1080p 60fps","fov":"90°","af":"HDR, Auto-focus","connect":"USB-C","mic":"Dual mic","type":"Webcam"}),
    ("Logitech C920s Pro HD Webcam","Logitech","Phụ kiện",1490000,1790000,{"resolution":"1080p 30fps","fov":"78°","af":"Autofocus","connect":"USB-A","mic":"Dual mic","type":"Webcam"}),
    ("Razer Kiyo Pro Ultra","Razer","Phụ kiện",5990000,6990000,{"resolution":"4K 30fps / 1080p 60fps","fov":"82°","af":"AI Focus","connect":"USB-C","mic":"–","type":"Webcam"}),
    # Microphone
    ("Blue Yeti X","Logitech","Phụ kiện",3490000,3990000,{"pattern":"4 pattern","sample":"48kHz/24bit","connect":"USB","type":"Condenser Mic","feature":"LED meter","weight":"519g"}),
    ("Rode NT-USB Mini","Rode","Phụ kiện",2290000,2690000,{"pattern":"Cardioid","sample":"48kHz/24bit","connect":"USB-C","type":"Condenser Mic","feature":"Headphone out","weight":"587g"}),
    ("HyperX SoloCast","HyperX","Phụ kiện",1190000,1490000,{"pattern":"Cardioid","sample":"48kHz/16bit","connect":"USB-C","type":"Condenser Mic","feature":"Tap-to-mute","weight":"261g"}),
    ("Elgato Wave:3","Elgato","Phụ kiện",3690000,4190000,{"pattern":"Cardioid","sample":"96kHz/24bit","connect":"USB-C","type":"Condenser Mic","feature":"Clipguard","weight":"280g"}),
    # Mouse pad
    ("Logitech Desk Mat Studio","Logitech","Phụ kiện",490000,590000,{"size":"700x300mm","material":"Polyester","feature":"Chống trượt","type":"Mouse Pad","weight":"–","connect":"–"}),
    ("Razer Gigantus V2 XXL","Razer","Phụ kiện",490000,590000,{"size":"940x410mm","material":"Micro-weave","feature":"Chống trượt","type":"Mouse Pad","weight":"–","connect":"–"}),
    # Laptop stand
    ("Rain Design mStand","Rain Design","Phụ kiện",1290000,1490000,{"material":"Nhôm nguyên khối","compatibility":"Laptop 10-17 inch","feature":"Tản nhiệt","type":"Laptop Stand","weight":"1.36kg","connect":"–"}),
    ("UGREEN Laptop Stand Aluminum","Ugreen","Phụ kiện",590000,790000,{"material":"Nhôm","compatibility":"Laptop 10-16 inch","feature":"Điều chỉnh góc, gập","type":"Laptop Stand","weight":"260g","connect":"–"}),
    # USB Hub / Dock
    ("Anker 577 Thunderbolt 4 Docking Station","Anker","Phụ kiện",5990000,6990000,{"ports":"Thunderbolt 4 x3, USB-A x4, HDMI, Ethernet, SD","power":"90W PD","type":"Docking Station","connect":"Thunderbolt 4","weight":"–","feature":"Triple display"}),
    ("CalDigit TS4 Thunderbolt 4 Dock","CalDigit","Phụ kiện",8490000,9490000,{"ports":"Thunderbolt 4 x3, USB-A x5, USB-C x3, HDMI, SD, 2.5GbE","power":"98W PD","type":"Docking Station","connect":"Thunderbolt 4","weight":"–","feature":"18 ports"}),
    ("Ugreen Revodok Pro 13-in-1 USB-C Hub","Ugreen","Phụ kiện",1690000,1990000,{"ports":"USB-C x2, USB-A x3, HDMI x2, RJ45, SD, 3.5mm","power":"100W PD","type":"USB-C Hub","connect":"USB-C","weight":"–","feature":"Dual HDMI 4K"}),
    ("Anker 332 USB-C Hub 5-in-1","Anker","Phụ kiện",490000,690000,{"ports":"USB-C, USB-A x2, HDMI, Ethernet","power":"–","type":"USB-C Hub","connect":"USB-C","weight":"–","feature":"4K HDMI"}),
    # Screen protector
    ("Dán cường lực Nillkin iPhone 16 Pro Max","Nillkin","Phụ kiện",190000,290000,{"material":"Kính cường lực 9H","compatibility":"iPhone 16 Pro Max","feature":"Full màn, chống vân tay","type":"Dán cường lực","weight":"–","connect":"–"}),
    ("Dán cường lực Samsung Galaxy S24 Ultra UV","Samsung","Phụ kiện",290000,390000,{"material":"Kính UV","compatibility":"Galaxy S24 Ultra","feature":"Full keo UV","type":"Dán cường lực","weight":"–","connect":"–"}),
    # Adapter
    ("Apple USB-C to Lightning Adapter","Apple","Phụ kiện",690000,890000,{"type":"Adapter","connect":"USB-C to Lightning","feature":"–","weight":"–","compatibility":"iPhone/iPad","power":"–"}),
    ("Apple USB-C Digital AV Multiport","Apple","Phụ kiện",1690000,1890000,{"type":"Adapter","connect":"USB-C to HDMI + USB-A + USB-C","feature":"4K 60Hz","weight":"–","compatibility":"Mac/iPad","power":"100W PD"}),
    # Apple Pencil
    ("Apple Pencil Pro","Apple","Phụ kiện",3490000,3990000,{"type":"Bút cảm ứng","connect":"Magnetic","feature":"Squeeze, Barrel Roll, Find My","weight":"–","compatibility":"iPad Pro M4, iPad Air M2","power":"–"}),
    ("Apple Pencil USB-C","Apple","Phụ kiện",2190000,2590000,{"type":"Bút cảm ứng","connect":"USB-C","feature":"Low latency, tilt","weight":"–","compatibility":"iPad 10, iPad Air, iPad Pro","power":"–"}),
    # AirTag
    ("Apple AirTag 4 Pack","Apple","Phụ kiện",2990000,3490000,{"type":"Tracker","connect":"Bluetooth + UWB","feature":"Find My, IP67","weight":"11g x4","compatibility":"iPhone","power":"CR2032"}),
    # Samsung accessories
    ("Samsung Galaxy SmartTag2 4 Pack","Samsung","Phụ kiện",1490000,1790000,{"type":"Tracker","connect":"Bluetooth + UWB","feature":"SmartThings Find, IP67","weight":"9g x4","compatibility":"Galaxy","power":"CR2032"}),
    # Router
    ("ASUS ROG Rapture GT-AX11000 Pro WiFi 6","ASUS","Phụ kiện",8990000,10490000,{"type":"Router","connect":"WiFi 6 AX11000","feature":"Tri-band, Gaming port 2.5G","weight":"–","compatibility":"–","power":"–"}),
    ("TP-Link Archer AX73 WiFi 6","TP-Link","Phụ kiện",1990000,2490000,{"type":"Router","connect":"WiFi 6 AX5400","feature":"Dual-band, OFDMA","weight":"–","compatibility":"–","power":"–"}),
    ("TP-Link Deco XE75 3-pack Mesh WiFi 6E","TP-Link","Phụ kiện",6990000,7990000,{"type":"Mesh WiFi","connect":"WiFi 6E AXE5400","feature":"Tri-band, AI-Driven Mesh","weight":"–","compatibility":"–","power":"–"}),
]

for item in EXTRA_ACCESSORIES:
    name, brand, cat, price, orig, specs = item
    add_product_if_new(name, cat, brand, price, orig, specs, random.choice([["Đen","Trắng"],["Đen"],["Trắng","Xám"]]), ["chất lượng cao","chính hãng","bảo hành"])

# ── If still under 1000, create more variants ──────────────
while len(new_products) < 1000:
    # Pick a random existing product and create a slight variant
    base = random.choice(new_products[70:])  # Only from new products
    suffix = random.choice([" - Phiên bản đặc biệt", " Limited Edition", " (Refurbished)", " Combo Edition", " Bundle Pack"])
    variant_name = base['name'] + suffix
    if variant_name in existing_names:
        continue
    existing_names.add(variant_name)
    price = int(base['price'] * random.uniform(0.75, 1.15))
    orig = int(base['original_price'] * random.uniform(0.85, 1.1))
    if orig <= price:
        orig = int(price * 1.15)
    p = create_product(next_id, variant_name, base['category'], base['brand'], price, orig, base['specs'], base['colors'], base['tags'])
    new_products.append(p)
    next_id += 1

# Trim to exactly 1000
new_products = new_products[:1000]

# ── Save ────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Total products: {len(new_products)}")
cat_counts = count_by_cat()
for c, n in sorted(cat_counts.items()):
    print(f"  {c}: {n}")

with open(f'{DATA_DIR}/products.json', 'w', encoding='utf-8') as f:
    json.dump(new_products, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved {len(new_products)} products to {DATA_DIR}/products.json")
