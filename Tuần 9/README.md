# Tuần 9 - Kết quả thực hành

## Lab 1: API Versioning

### Test v1 và Sunset header

Gọi `GET /api/v1/users/1`: trả HTTP 200, thông tin user có `full_name` và header `Sunset`.

![1794985983762](image/README/1794985983762.png)

<!-- Thêm ảnh test v1 tại đây -->

### Test v2

Gọi `GET /api/v2/users/1`: trả HTTP 200, thông tin user có `first_name` và `last_name`.

![1794985999765](image/README/1794985999765.png)

<!-- Thêm ảnh test v2 tại đây -->

### Test user không tồn tại

Gọi `GET /api/v1/users/999`: trả HTTP 404.

![1794986012716](image/README/1794986012716.png)

<!-- Thêm ảnh test 404 tại đây -->

### Test tạo user

Gọi `POST /api/v2/users` với `first_name`, `last_name`, `email`: trả HTTP 201 và user vừa tạo. Có thể gọi GET theo ID mới ở cả v1 và v2.

![1794986031300](image/README/1794986031300.png)![1794986051602](image/README/1794986051602.png)

<!-- Thêm ảnh test POST và GET user mới tại đây -->

### Test dữ liệu không hợp lệ

Gọi `POST /api/v2/users` với dữ liệu thiếu hoặc rỗng: trả HTTP 400.![1794986084976](image/README/1794986084976.png)

<!-- Thêm ảnh test dữ liệu không hợp lệ tại đây -->

## Lab 2: Header Versioning

- Không gửi header: `GET /users/1` trả v2 và `X-API-Version-Served: 2`.
- ![1794986509714](image/README/1794986509714.png)
- Gửi `X-API-Version: 1`: trả `full_name` và header xác nhận phiên bản 1.
- ![1794986523477](image/README/1794986523477.png)
- Gửi `X-API-Version: 2024-06-20`: trả dữ liệu theo phiên bản ngày.
- ![1794986542601](image/README/1794986542601.png)
- Gửi `X-API-Version: 99`: trả HTTP 400.
- Gọi user không tồn tại: trả HTTP 404.

<!-- Thêm ảnh kiểm thử Lab 2 tại đây -->

## Lab 3: Sunset Middleware

- Gọi `GET /api/v1/users/1` trước mốc sunset (31/12/2026 lúc 23:59:59 UTC) trả HTTP 200, có `full_name` và các header `Sunset`, `Deprecation` và `Link`.

![1795530257101](image/README/1795530257101.png)

- Gọi từ mốc sunset trở đi trả HTTP 410 với `error` là `gone` và `use_instead` là `/api/v2/users`.

![1795530265146](image/README/1795530265146.png)

- Mỗi lần gọi v1 ghi log `deprecated_call` kèm đường dẫn và địa chỉ IP.

![1795530302079](image/README/1795530302079.png)

<!-- Thêm ảnh kiểm thử Lab 3 tại đây -->

## Lab 4: Blue-Green Routing

- Gọi `POST /orders` với `X-Cohort: beta` hoặc `internal` trả HTTP 201 và `X-Order-Handler: v2`.
  ![1795529088298](image/README/1795529088298.png)
- Tài khoản `acct_42` hoặc `acct_99` trong allow-list cũng được chuyển sang v2.
  ![1795529104236](image/README/1795529104236.png)
- Ở mức rollout 5%, `customer_195` thuộc bucket 4 nên trả HTTP 201 (v2). `customer_69` thuộc bucket 5 nên trả HTTP 200 (v1).
- ![1795529118704](image/README/1795529118704.png)
- Khi đặt `V2_PERCENT=100`, gọi lại với `customer_69` trả HTTP 201 và `X-Order-Handler: v2`.
- ![1795529129340](image/README/1795529129340.png)

<!-- Thêm ảnh kiểm thử Lab 4 tại đây -->
