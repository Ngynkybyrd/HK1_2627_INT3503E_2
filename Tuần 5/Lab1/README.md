# Bài 1 — Resource Design: Hệ thống quản lý thư viện

## 1. Giới thiệu

Bài tập tập trung vào thiết kế tài nguyên (Resource Design) cho một hệ thống quản lý thư viện, sử dụng các nguyên tắc thiết kế RESTful API và mô hình hóa dữ liệu.

**Mục tiêu:**
- Xây dựng sơ đồ thực thể – mối quan hệ (ERD).
- Xác định tập tài nguyên (Resource Set) của hệ thống.
- Thiết kế danh sách từ 12 đến 20 API endpoints.
- Xây dựng JSON Schema cho 3 tài nguyên chính.

## 2. Mô tả hệ thống

Hệ thống quản lý thư viện hỗ trợ quản lý thông tin đầu sách, tác giả, các bản sao sách vật lý, độc giả và hoạt động mượn/trả sách.

Các chức năng chính:
- Quản lý thông tin sách và tác giả.
- Theo dõi từng bản sao vật lý của một đầu sách.
- Quản lý thông tin độc giả.
- Ghi nhận lượt mượn và trả sách.
- Tra cứu lịch sử mượn sách.

### Phạm vi và giả định nghiệp vụ

- Một đầu sách có thể có nhiều tác giả; một tác giả có thể viết nhiều đầu sách.
- Một đầu sách có thể có nhiều bản sao vật lý.
- Mỗi bản sao thuộc về đúng một đầu sách.
- Một độc giả có thể có nhiều lượt mượn.
- Mỗi lượt mượn gắn với đúng một độc giả và một bản sao sách.
- Một bản sao không được có nhiều lượt mượn chưa trả cùng lúc.
- Lịch sử mượn/trả được lưu lại sau khi giao dịch hoàn tất.

Các chức năng đăng nhập, đặt trước sách, tính tiền phạt và thanh toán không thuộc phạm vi của phiên bản này.

## 3. Sơ đồ ERD

ERD gồm 6 thực thể:

| Thực thể | Mô tả |
|---|---|
| `BOOK` | Lưu thông tin chung của một đầu sách. |
| `AUTHOR` | Lưu thông tin tác giả. |
| `BOOK_AUTHOR` | Bảng nối thể hiện quan hệ nhiều-nhiều giữa sách và tác giả. |
| `BOOK_COPY` | Đại diện cho từng bản sao sách vật lý. |
| `MEMBER` | Lưu thông tin độc giả. |
| `LOAN` | Lưu thông tin các lượt mượn và trả sách. |

### Sơ đồ

![Sơ đồ ERD hệ thống quản lý thư viện](diagrams/library-erd.png)

File nguồn có thể chỉnh sửa bằng draw.io: [`library-erd.drawio`](diagrams/library-erd.drawio).

### Các quan hệ chính

- `BOOK` – `BOOK_AUTHOR`: quan hệ một-nhiều.
- `AUTHOR` – `BOOK_AUTHOR`: quan hệ một-nhiều.
- `BOOK` – `BOOK_COPY`: quan hệ một-nhiều.
- `MEMBER` – `LOAN`: quan hệ một-nhiều.
- `BOOK_COPY` – `LOAN`: quan hệ một-nhiều theo lịch sử mượn.

Quan hệ nhiều-nhiều giữa `BOOK` và `AUTHOR` được triển khai thông qua bảng nối `BOOK_AUTHOR`, với khóa chính ghép gồm `book_id` và `author_id`.

## 4. Tập tài nguyên (Resource Set)

API sử dụng các tài nguyên chính sau:

| Tài nguyên | URL cơ sở | Mục đích |
|---|---|---|
| Sách (`Books`) | `/api/v1/books` | Quản lý thông tin đầu sách. |
| Tác giả (`Authors`) | `/api/v1/authors` | Quản lý thông tin tác giả. |
| Bản sao sách (`Book Copies`) | `/api/v1/book-copies` | Quản lý từng cuốn sách vật lý. |
| Độc giả (`Members`) | `/api/v1/members` | Quản lý thông tin độc giả. |
| Lượt mượn (`Loans`) | `/api/v1/loans` | Quản lý lượt mượn và trả sách. |

Quan hệ giữa sách và tác giả được truy cập thông qua các endpoint lồng nhau của tài nguyên sách, thay vì cung cấp một URL cơ sở riêng cho bảng nối `BOOK_AUTHOR`.

## 5. Danh sách API endpoints

API sử dụng tiền tố `/api/v1` để thể hiện phiên bản. Các URL dưới đây là thiết kế đề xuất, không phải các endpoint đã được triển khai.

| STT | HTTP Method | Endpoint | Mô tả |
|---:|---|---|---|
| 1 | GET | `/api/v1/books` | Lấy danh sách sách. |
| 2 | POST | `/api/v1/books` | Tạo đầu sách mới. |
| 3 | GET | `/api/v1/books/{bookId}` | Lấy thông tin chi tiết một đầu sách. |
| 4 | PATCH | `/api/v1/books/{bookId}` | Cập nhật một phần thông tin sách. |
| 5 | DELETE | `/api/v1/books/{bookId}` | Xóa đầu sách khi đáp ứng điều kiện nghiệp vụ. |
| 6 | GET | `/api/v1/authors` | Lấy danh sách tác giả. |
| 7 | POST | `/api/v1/authors` | Tạo tác giả mới. |
| 8 | GET | `/api/v1/authors/{authorId}` | Lấy thông tin chi tiết tác giả. |
| 9 | GET | `/api/v1/books/{bookId}/authors` | Lấy danh sách tác giả của một đầu sách. |
| 10 | PUT | `/api/v1/books/{bookId}/authors/{authorId}` | Thiết lập liên kết giữa sách và tác giả. |
| 11 | GET | `/api/v1/members` | Lấy danh sách độc giả. |
| 12 | POST | `/api/v1/members` | Đăng ký độc giả mới. |
| 13 | GET | `/api/v1/members/{memberId}` | Lấy thông tin chi tiết độc giả. |
| 14 | PATCH | `/api/v1/members/{memberId}` | Cập nhật thông tin độc giả. |
| 15 | GET | `/api/v1/book-copies/{copyId}` | Lấy thông tin chi tiết một bản sao sách. |
| 16 | GET | `/api/v1/loans` | Tra cứu và lọc các lượt mượn. |
| 17 | POST | `/api/v1/loans` | Tạo lượt mượn sách. |
| 18 | POST | `/api/v1/loans/{loanId}/return` | Ghi nhận việc trả sách. |

**Tổng số: 18 endpoints**, đáp ứng yêu cầu từ 12 đến 20 endpoints.

## 6. JSON Schema

Các JSON Schema mô tả cấu trúc dữ liệu và các quy tắc kiểm tra cơ bản cho ba tài nguyên chính.

| Tài nguyên | File | Mô tả |
|---|---|---|
| Book | [`book.schema.json`](schemas/book.schema.json) | Cấu trúc dữ liệu của đầu sách. |
| Member | [`member.schema.json`](schemas/member.schema.json) | Cấu trúc dữ liệu của độc giả. |
| Loan | [`loan.schema.json`](schemas/loan.schema.json) | Cấu trúc dữ liệu của lượt mượn. |

Các schema quy định kiểu dữ liệu, trường bắt buộc và những ràng buộc phù hợp với từng tài nguyên. Chúng cần được giữ nhất quán với mô hình ERD.

## 7. Các quyết định thiết kế

### 7.1. Tách đầu sách và bản sao sách

`BOOK` lưu thông tin chung của đầu sách, trong khi `BOOK_COPY` đại diện cho từng cuốn sách vật lý. Cách thiết kế này cho phép quản lý tình trạng và lịch sử mượn của từng cuốn riêng biệt.

### 7.2. Sử dụng bảng nối cho quan hệ sách – tác giả

Do một đầu sách có thể có nhiều tác giả và một tác giả có thể viết nhiều đầu sách, quan hệ nhiều-nhiều được triển khai thông qua `BOOK_AUTHOR`. Hai trường `book_id` và `author_id` đồng thời tạo thành khóa chính ghép và là các khóa ngoại tham chiếu đến hai bảng tương ứng.

### 7.3. Lưu lịch sử mượn/trả

`LOAN` lưu thời điểm mượn, hạn trả và thời điểm trả thực tế. Trường `returned_at` cho phép nhận giá trị `NULL` khi lượt mượn chưa hoàn tất. Các bản ghi cũ được giữ lại để phục vụ tra cứu lịch sử.

### 7.4. Thiết kế URL theo RESTful

URL sử dụng danh từ số nhiều để biểu diễn tài nguyên. HTTP method xác định thao tác, còn tham số đường dẫn dùng để xác định tài nguyên cụ thể.

Các thao tác nghiệp vụ như trả sách được biểu diễn bằng endpoint riêng để thể hiện rõ hành động và cho phép hệ thống kiểm tra các điều kiện nghiệp vụ liên quan.

## 8. Các tệp bàn giao

- [Tài liệu Resource Design (PDF)](resource-design.pdf)
- [Sơ đồ ERD (PNG)](diagrams/library-erd.png)
- [File ERD có thể chỉnh sửa](diagrams/library-erd.drawio)
- [Book JSON Schema](schemas/book.schema.json)
- [Member JSON Schema](schemas/member.schema.json)
- [Loan JSON Schema](schemas/loan.schema.json)

## 9. Kết luận

Bài tập xây dựng mô hình dữ liệu và thiết kế RESTful API cho hệ thống quản lý thư viện trong phạm vi quản lý sách, tác giả, bản sao sách, độc giả và nghiệp vụ mượn/trả.

Thiết kế hướng đến sự nhất quán giữa ERD, Resource Set, URL List và JSON Schema, đồng thời giới hạn phạm vi ở các nghiệp vụ cốt lõi để phù hợp với yêu cầu bài tập.
