# Báo cáo phân tích dữ liệu TechStore AI

- Thời gian tạo báo cáo: 2026-03-15 12:44:15
- Nguồn dữ liệu: data/products.json, data/csv/synthetic_400k.csv, data/csv/reviews_300k.csv, data/csv/behavior_logs_200k.csv

## 1) Quy mô dữ liệu
- Sản phẩm: **20,000**
- Người dùng (unique theo orders): **49,985**
- Đơn hàng: **400,000**
- Reviews: **300,000**
- Behavior logs: **200,000**

## 2) KPI kinh doanh chính
- Tổng doanh thu: **10,402.81 tỷ VND**
- AOV (giá trị đơn hàng trung bình): **26.01 triệu VND**
- Tỷ lệ hoàn trả: **5.03%**
- Rating trung bình từ orders: **4.05/5**
- Rating trung bình từ reviews: **4.14/5**

## 3) Khoảng thời gian dữ liệu
- Orders: **01/01/2023 → 31/12/2024**
- Reviews: **01/01/2023 → 31/12/2024**
- Behavior logs: **01/01/2023 → 31/12/2024**

## 4) Top danh mục theo doanh thu
- 1. Laptop: **4,327.67 tỷ VND**
- 2. Điện thoại: **1,927.41 tỷ VND**
- 3. Máy ảnh: **1,179.22 tỷ VND**
- 4. Màn hình: **1,146.63 tỷ VND**
- 5. Phụ kiện: **631.96 tỷ VND**
- 6. Máy tính bảng: **529.58 tỷ VND**
- 7. Đồng hồ thông minh: **412.18 tỷ VND**
- 8. Lưu trữ: **248.16 tỷ VND**

## 5) Top danh mục theo số đơn
- 1. Laptop: **88,593 đơn**
- 2. Phụ kiện: **81,837 đơn**
- 3. Điện thoại: **80,510 đơn**
- 4. Màn hình: **41,919 đơn**
- 5. Đồng hồ thông minh: **30,664 đơn**
- 6. Lưu trữ: **30,243 đơn**
- 7. Máy ảnh: **24,963 đơn**
- 8. Máy tính bảng: **21,271 đơn**

## 6) Cơ cấu thanh toán và thiết bị
### Thanh toán
- Thẻ tín dụng: **23.85%**
- Ví MoMo: **19.72%**
- Chuyển khoản ngân hàng: **17.01%**
- VNPay: **15.45%**
- Ví ZaloPay: **13.86%**
- COD: **10.11%**

### Thiết bị
- Mobile: **49.15%**
- Desktop: **38.36%**
- Tablet: **12.49%**

## 7) Chất lượng review và hành vi
### Phân bố rating reviews
- 1 sao: **3.04%**
- 2 sao: **5.01%**
- 3 sao: **11.88%**
- 4 sao: **35.09%**
- 5 sao: **44.98%**

### Phân bố hành vi (action_type)
- view: **35.01%**
- click: **24.86%**
- search: **15.02%**
- add_to_cart: **12.1%**
- compare: **5.03%**
- wishlist: **4.95%**
- share: **3.02%**

## 8) Dữ liệu thiếu (missing values)
| Dataset | Missing values | Missing rate (%) |
|---|---:|---:|
| products | 0 | 0.0000 |
| orders_400k | 620,209 | 4.4301 |
| reviews_300k | 396,860 | 8.8191 |
| behavior_200k | 260,082 | 8.1276 |

## 9) Nhận định nhanh
- Dữ liệu có quy mô lớn, đủ để huấn luyện các mô hình gợi ý và phân tích hành vi.
- Cần theo dõi song song rating_order và rating reviews để tránh lệch cảm nhận chất lượng.
- Cơ cấu payment/device và tỷ lệ hoàn trả là các biến quan trọng cho tối ưu vận hành.