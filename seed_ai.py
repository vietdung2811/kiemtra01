import requests
import json

AI_API_URL = "http://ai-service:8005/api/track-view/"

# Giả lập người dùng (user_id=1) đã xem một số sản phẩm để AI có cơ sở gợi ý
fake_views = [
    {
        "user_id": 1,
        "product_id": 6,
        "product_type": "laptop",
        "brand": "Apple",
        "name": "MacBook Pro 16",
        "price": 2499.99,
        "description": "M3 Max, 32GB RAM, 1TB SSD"
    },
    {
        "user_id": 1,
        "product_id": 1,
        "product_type": "mobile",
        "brand": "Apple",
        "name": "Iphone 15",
        "price": 1000.00,
        "description": "flagship"
    },
    {
        "user_id": 1,
        "product_id": 6,
        "product_type": "mobile",
        "brand": "Xiaomi",
        "name": "Xiaomi 14 Ultra",
        "price": 1199.00,
        "description": "Leica Optics, 1-inch sensor"
    }
]

print("Đang tạo dữ liệu giả cho AI Service...")
for view in fake_views:
    try:
        response = requests.post(AI_API_URL, json=view)
        if response.status_code == 201:
            print(f"Thành công: Đã log lượt xem cho {view['name']}")
        else:
            print(f"Thất bại: {view['name']} - {response.status_code}")
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

print("Hoàn tất! Bây giờ khi bạn vào trang tìm kiếm với user_id=1, AI sẽ gợi ý các sản phẩm cùng hãng Apple và Xiaomi mà bạn chưa xem.")
