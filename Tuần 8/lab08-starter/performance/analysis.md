# Lab 4 — Phân tích kết quả Locust

## Thiết lập

Đo ngày 17/11/2026 trên Windows, Python 3.13.5, Locust 2.47.0; Flask development server và Locust chạy trên cùng máy qua 127.0.0.1. Mỗi kịch bản dùng một database SQLite ban đầu rỗng riêng; API dùng cổng 18574. Các tác vụ có trọng số list/read/create/search lần lượt 3/2/1/1, thời gian chờ giữa các tác vụ là 1–3 giây. Mỗi lượt chạy một lần; thời gian có bao gồm giai đoạn tăng số users.

| Kịch bản | Users | Spawn rate (users/s) | Thời lượng | Requests | p95 tổng hợp (ms) | Failure rate | RPS trung bình |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 135 | 11 | 0/135 (0%) | 4,63 |
| B | 50 | 5 | 60s | 1.376 | 11 | 0/1.376 (0%) | 23,17 |
| C | 200 | 50 | 30s | 2.894 | 66 | 0/2.894 (0%) | 97,93 |

Số liệu là tổng hợp cuối cùng trong log `reports/lab4_A.log`, `lab4_B.log` và `lab4_C.log`; p95 là giá trị xấp xỉ do Locust tính. RPS là Requests/s tổng hợp Locust báo, không phải số users. CSV là ảnh chụp lúc xuất báo cáo. Các file A.html và B.html đã được chạy lại sau phép đo trong bảng; C.html là ảnh chụp của lượt đo trong bảng, còn C.htm là báo cáo của lần chạy sau. Ở C, một số request hoàn tất trong lúc dừng: CSV ghi 2.883 request, p95 64 ms và 98,67 RPS; log cuối ghi 2.894, 66 ms và 97,93 RPS. Vì vậy bảng dùng nhất quán log cuối, không trộn hai ảnh chụp.

## Nhận xét

1. **C có p95 cao nhất:** 66 ms so với 11 ms ở cả A và B. Trong C, p95 theo log của `GET /books` là 73 ms, `GET /books/{id}` 58 ms, tìm theo năm 44 ms, và `POST /books` 84 ms. Độ trễ tăng khi tải cao hơn, nhưng một lượt chạy không đủ để xác định nguyên nhân hoặc chứng minh quan hệ nhân quả.
2. Không có endpoint nào tăng failure rate trong các lượt đo: cả bốn nhóm đều có 0 lỗi. Không chèn lỗi giả lập 1%, nên không có failure do `response.failure()` được cố ý tạo; lỗi HTTP thực (ví dụ server trả 500) khác với lỗi do Locust đánh dấu phía client. Riêng `GET /books/{id}` coi 404 là kết quả dự kiến vì ID được chọn ngẫu nhiên; 404 này không được tính vào failure rate. Kết quả 0% vì thế không có nghĩa mọi response đều là 2xx.
3. Với SLO giả định p95 **< 300 ms**, cả A, B và C đều đạt trên mẫu đo tổng hợp này (11, 11, 66 ms). Đây không chứng minh SLO production: mỗi kịch bản chỉ chạy một lần, thời gian ngắn, có ramp-up, dữ liệu nhỏ, tải ngẫu nhiên, client và server cùng máy, Flask development server và SQLite không đại diện môi trường production. p95 tổng hợp còn phụ thuộc tỷ lệ endpoint; cần xem từng endpoint và lặp lại nhiều lần.
4. Để kiểm tra pool giới hạn 5: cấu hình pool thực sự có `pool_size=5`, `max_overflow=0` và `pool_timeout` rõ ràng; xác nhận engine và phiên bản SQLite/SQLAlchemy đang dùng hỗ trợ cấu hình này. So sánh với pool lớn hơn trong cùng điều kiện, dữ liệu, cấu hình client và thời lượng; chạy lặp nhiều lần, ghi p95 từng endpoint, RPS, lỗi timeout và thời gian chờ lấy connection (instrument pool). Đảm bảo các lượt có đủ tải đồng thời để tranh chấp pool; không suy ra ảnh hưởng chỉ từ cấu hình.

## File kết quả

- `reports/A.html`, `B.html`, `C.html`: báo cáo Locust.
- `reports/lab4_{A,B,C}.log`: thống kê cuối và log chạy.
- `reports/lab4_{A,B,C}_stats.csv`, `_failures.csv`, `_exceptions.csv`, `_stats_history.csv`: số liệu xuất từ Locust. Các file `.db` cùng tên là dữ liệu riêng được tạo trong lúc đo, không cần đưa vào Git.
