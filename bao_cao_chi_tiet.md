# HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG
## KHOA CÔNG NGHỆ THÔNG TIN 1

---

# KIẾN TRÚC VÀ THIẾT KẾ PHẦN MỀM
## TIỂU LUẬN FINAL

**Sinh viên thực hiện:** Nguyễn Bá Việt Hoàng (B22DCVT210)
**Ngày hoàn thành:** 05/06/2026

---

## MỤC LỤC
(Tự động cập nhật trong Word)

---

## CHƯƠNG 1. TỪ MONOLITHIC ĐẾN MICROSERVICES VÀ DDD

### 1.1. GIỚI THIỆU MONOLITHIC ARCHITECTURE
#### 1.1.1. Khái niệm
Monolithic Architecture (kiến trúc nguyên khối) là mô hình truyền thống trong đó toàn bộ chức năng của ứng dụng (UI, Business Logic, Data Access) được đóng gói và triển khai như một đơn vị duy nhất. Mọi thành phần chạy chung trong một tiến trình và chia sẻ cùng một mã nguồn.

#### 1.1.2. Cấu trúc điển hình
Thường được tổ chức theo mô hình phân tầng (Layered Architecture):
- **Presentation Layer:** Xử lý giao diện và API endpoint.
- **Business Logic Layer:** Thực hiện các quy tắc nghiệp vụ.
- **Data Access Layer:** Tương tác với DB (thường là Shared Database).

[HÌNH 1: Cấu trúc điển hình của Monolithic]

#### 1.1.3. Nhược điểm chi tiết
- **Khó mở rộng:** Phải scale toàn bộ ứng dụng thay vì từng phần nhỏ.
- **Tight Coupling:** Lỗi ở một module (ví dụ: giỏ hàng) có thể làm sập toàn bộ hệ thống.
- **Kém linh hoạt:** Ràng buộc chặt chẽ vào một stack công nghệ duy nhất.
- **Triển khai rủi ro:** Mỗi thay đổi nhỏ đều yêu cầu build và deploy lại toàn bộ project.

### 1.2. MICROSERVICES ARCHITECTURE
#### 1.2.1. Khái niệm
Là kiến trúc chia nhỏ hệ thống thành các dịch vụ (services) độc lập. Mỗi service quản lý một domain nghiệp vụ riêng, có cơ sở dữ liệu riêng (Database per Service) và giao tiếp qua mạng (REST/gRPC).

#### 1.2.2. Ưu điểm
- **Scale độc lập:** Chỉ tăng tải cho service cần thiết (ví dụ: Product Service).
- **Cô lập lỗi:** Lỗi ở AI Service không ảnh hưởng đến luồng thanh toán.
- **Đa dạng công nghệ:** Mỗi service có thể dùng ngôn ngữ/DB phù hợp nhất.

[HÌNH 2: So sánh cấu trúc triển khai Monolithic và Microservices]

### 1.3. DOMAIN DRIVEN DESIGN (DDD)
#### 1.3.1. Các khái niệm cốt lõi
- **Entity:** Đối tượng có định danh (ID) duy nhất (ví dụ: User, Product).
- **Value Object:** Đối tượng mô tả thuộc tính, không cần ID (ví dụ: Address, Money).
- **Aggregate:** Cụm các Entity/Value Object liên quan, quản lý qua Aggregate Root (ví dụ: Order là Root của OrderItem).
- **Bounded Context:** Ranh giới logic nơi các mô hình và thuật ngữ có ý nghĩa nhất quán.

[HÌNH 3: Context Map trong hệ Pharma E-Commerce]

---

## CHƯƠNG 2. PHÁT TRIỂN HỆ E-COMMERCE MICROSERVICES

### 2.1. XÁC ĐỊNH YÊU CẦU
- **Yêu cầu chức năng (FR):** Đăng ký/đăng nhập, tìm kiếm sản phẩm dược, tư vấn AI, quản lý giỏ hàng, thanh toán (COD/Sandbox), theo dõi đơn hàng.
- **Yêu cầu phi chức năng (NFR):** Tính sẵn sàng cao, an toàn tư vấn dược phẩm (RAG có nguồn), bảo mật JWT.

### 2.2. PHÂN RÃ HỆ THỐNG THEO DDD
Dựa trên nghiệp vụ Pharma, hệ thống được chia thành các Bounded Context:
1. **Catalog Context (Product Service):** Quản lý dược phẩm, tồn kho.
2. **Identity Context (User Service):** Quản lý tài khoản, JWT.
3. **Ordering Context (Order Service):** Xử lý đơn hàng, snapshot giá.
4. **Basket Context (Cart Service):** Giỏ hàng tạm thời.
5. **AI Consultation Context (AI Service):** Tư vấn Deep Learning/RAG.

[HÌNH 4: Sơ đồ phân rã Service (Service Decomposition Diagram)]

### 2.3. THIẾT KẾ CHI TIẾT CÁC SERVICE (DJANGO)
#### 2.3.1. Product Service
- **Model:** `Product`, `Category`, `Brand`. Sử dụng `JSONField` để lưu thuộc tính dược phẩm linh hoạt (thành phần, chống chỉ định).
- **API:** `GET /products/`, `POST /products/internal/reserve-stock/` (API nội bộ để giữ hàng).

[HÌNH 5: Biểu đồ lớp (Class Diagram) - Product Service]

#### 2.3.2. Order Service & Workflow Checkout
Luồng checkout quan trọng nhất:
1. Nhận yêu cầu từ Gateway.
2. Gọi Product Service để `reserve-stock`.
3. Nếu thành công, tạo `Order` và `OrderItem` (snapshot giá/tên).
4. Phản hồi xác nhận và yêu cầu Cart Service xóa giỏ hàng.

[HÌNH 6: Sequence Diagram - Luồng Mua hàng và Reserve Stock]

---

## CHƯƠNG 3. AI SERVICE CHO TƯ VẤN SẢN PHẨM

### 3.1. KIẾN TRÚC AI HYBRID
Hệ thống AI không chỉ là chatbot đơn thuần mà kết hợp 3 thành phần:
1. **Deep Learning (LSTM):** Dự đoán danh mục quan tâm từ chuỗi hành vi người dùng (view -> search -> add_to_cart).
2. **Knowledge Graph (Neo4j):** Biểu diễn mối quan hệ Thuốc - Triệu chứng - Hoạt chất - Chống chỉ định.
3. **RAG (Retrieval-Augmented Generation):** Truy xuất thông tin từ Knowledge Base (file PDF/Dược điển) để trả lời có căn cứ.

[HÌNH 7: Pipeline AI Service (LSTM + Neo4j + RAG)]

### 3.2. MÔ HÌNH LSTM (SEQUENCE MODELING)
- **Dữ liệu:** Chuỗi hành động người dùng dạng `action:value`.
- **Mục tiêu:** Phân loại đa lớp (Multi-class classification) để gợi ý danh mục sản phẩm tiếp theo.
- **Kết quả:** Đạt Accuracy ~85-90% trên tập dữ liệu thử nghiệm.

[HÌNH 8: Biểu đồ so sánh hiệu năng các mô hình RNN, LSTM, BiLSTM]

### 3.3. KNOWLEDGE GRAPH VỚI NEO4J
Sử dụng Cypher để truy vấn an toàn dược phẩm. Ví dụ: "Thuốc X có chứa hoạt chất Y gây tương tác với thuốc Z không?".

[HÌNH 9: Giao diện Neo4j Browser hiển thị đồ thị thuốc - triệu chứng]

---

## CHƯƠNG 4. XÂY DỰNG HỆ THỐNG HOÀN CHỈNH

### 4.1. KIẾN TRÚC TỔNG THỂ
- **Frontend:** React/Vite.
- **API Gateway:** Django (Entry point duy nhất, xử lý Auth/Routing).
- **Backend:** Các Microservices chạy trong container Docker riêng biệt.
- **Database:** PostgreSQL cho dữ liệu quan hệ, Neo4j cho đồ thị.

[HÌNH 10: Kiến trúc triển khai toàn hệ thống (Deployment Architecture)]

### 4.2. AUTHENTICATION (JWT)
Sử dụng JWT chuẩn HS256. Gateway giải mã token, kiểm tra `iss`, `exp` và forward thông tin `user_id/role` qua HTTP Header xuống các service nội bộ.

### 4.3. DOCKER HÓA HỆ THỐNG
Tất cả các thành phần được định nghĩa trong `docker-compose.yml`, chia theo network nội bộ để đảm bảo an toàn.

[HÌNH 11: Screenshot Docker Desktop/Terminal hiển thị các container đang chạy]

---

## KẾT LUẬN VÀ TỰ ĐÁNH GIÁ
Đề tài đã hoàn thành việc chuyển đổi tư duy từ Monolithic sang Microservices, áp dụng thành công DDD để phân rã hệ thống và tích hợp AI Service thực tế. Điểm mạnh là hệ thống có nghiệp vụ thật (giảm tồn kho, JWT thật) thay vì chỉ mô phỏng giao diện.

**Hướng phát triển:** Tích hợp Redis cho caching, triển khai ELK Stack để giám sát log tập trung.

---
**HẾT**
