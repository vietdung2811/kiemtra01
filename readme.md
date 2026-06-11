# 1. Vào thư mục dự án
cd /home/vietdung2811/Documents/kiemtra01
# 2. Build và khởi động tất cả services
docker-compose up --build -d
# 3. Chạy migrations
docker exec customer_service python manage.py migrate
docker exec staff_service python manage.py migrate
docker exec laptop_service python manage.py migrate
docker exec mobile_service python manage.py migrate
docker exec ai-service python manage.py migrate
# 4. Seed dữ liệu sản phẩm + AI
docker cp seed_products.py ai-service:/app/seed_products.py
docker cp seed_ai.py ai-service:/app/seed_ai.py
docker exec ai-service python /app/seed_products.py
docker exec ai-service python /app/seed_ai.py
docker exec ai-service python /app/build_kb_graph.py
🌐 URL truy cập
Service	URL
Customer (mua hàng)	http://localhost/customer/
Staff (quản lý)	http://localhost/staff/
API Gateway	http://localhost:8000
Neo4j Browser	http://localhost:7474
👤 Tài khoản người dùng
Hiện chưa có tài khoản mẫu được tạo sẵn. Bạn cần tạo bằng lệnh sau:

bash
# Tạo superuser cho Customer Service
docker exec -it customer_service python manage.py createsuperuser
# Tạo superuser cho Staff Service
docker exec -it staff_service python manage.py createsuperuser