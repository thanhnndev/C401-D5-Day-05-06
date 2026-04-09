# Tài liệu HTTP API — LangGraph (chat & lịch sử phiên)

---

## Mục đích

- **Chat:** gửi một lượt tin nhắn người dùng, chạy graph một vòng, nhận state đầu ra và giữ nhất quán theo **thread** (phiên hội thoại).
- **Lịch sử:** đọc các checkpoint của một thread để hiển thị timeline / debug (dữ liệu đến từ LangGraph `get_state_history`).

---

## Địa chỉ cơ sở và OpenAPI

- **Base URL:** do môi trường triển khai quy định (ví dụ `http://localhost:8000` khi chạy `uvicorn` cục bộ). Mọi đường dẫn dưới đây là **relative** từ base URL.
- **OpenAPI / Swagger UI:** `GET /docs` — có thể dùng để đối chiếu schema và thử request trong trình duyệt (chỉ khi server bật tài liệu tương tác).
- **OpenAPI JSON:** `GET /openapi.json` — phù hợp để sinh client types hoặc import vào Postman.

---

## Định dạng chung

- Các endpoint nhận/gửi JSON dùng kiểu nội dung **`application/json`** (trừ khi ghi chú khác).
- **Không có xác thực người dùng** trong phiên bản hiện tại: mọi client có thể gọi nếu tiếp cận được URL. Nếu triển khai production, cần bổ sung lớp bảo vệ (reverse proxy, API key, v.v.) ở tầng hạ tầng hoặc trong app.
- **CORS:** ứng dụng hiện tại **chưa** cấu hình middleware CORS mặc định. Trình duyệt gọi trực tiếp từ domain khác có thể bị chặn bởi policy trình duyệt; thường giải quyết bằng proxy cùng origin hoặc bật CORS phía server khi cần.

---

## Thread ID (phiên hội thoại)

- **`thread_id`** xác định một luồng checkpoint riêng trên server (map với `configurable.thread_id` của LangGraph).
- **Gửi chat:** nếu client **không** gửi `thread_id`, server **tự sinh** một UUID và trả lại trong response — client nên **lưu** giá trị này và dùng lại cho các tin tiếp theo trong cùng cuộc hội thoại.
- **Lịch sử:** chỉ định thread qua path parameter như mô tả endpoint bên dưới.

---

## Endpoint: kiểm tra sống (health)

| Thuộc tính | Giá trị |
|------------|---------|
| Phương thức & đường dẫn | `GET /health` |
| Body | Không |

**Phản hồi thành công (HTTP 200):** JSON object gồm:

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `status` | string | Luôn là `"ok"` khi process trả lời được (liveness của API). |
| `databases` | object | Hai khóa con: `academic` và `ctsv` — mỗi khóa mô tả **một** instance PostgreSQL theo biến môi trường tương ứng. |

**Một instance trong `databases` (ví dụ `databases.academic`):**

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `configured` | boolean | `true` nếu biến môi trường URL cho instance đó được set (không rỗng). `academic` ↔ `DATABASE_URL`; `ctsv` ↔ `CTSV_DATABASE_URL`. |
| `reachable` | boolean hoặc `null` | `null` khi `configured` là `false` (không probe). `true` nếu thực hiện được truy vấn kiểm tra đơn giản (`SELECT 1`). `false` nếu đã cấu hình nhưng kết nối thất bại. |
| `error` | string hoặc `null` | Chỉ có ý nghĩa khi `configured` là `true` và `reachable` là `false`: thông báo lỗi rút gọn từ driver (tối đa ~500 ký tự). |

**Mục đích:** vừa probe liveness của API, vừa cho frontend/ops biết trạng thái hai DB logic (học vụ và CTSV) **tại thời điểm gọi** — không thay cho giám sát DB chuyên dụng.

---

## Endpoint: chat

| Thuộc tính | Giá trị |
|------------|---------|
| Phương thức & đường dẫn | `POST /chat` |
| Body (JSON) | Xem bảng **ChatRequest** bên dưới |

### ChatRequest (body)

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|--------|
| `message` | string | Có | Nội dung người dùng; độ dài tối thiểu 1 ký tự. Được map vào state graph với khóa `text`. |
| `thread_id` | string hoặc `null` | Không | Định danh phiên. Bỏ trống hoặc `null` thì server sinh UUID mới. |

### ChatResponse (phản hồi thành công, HTTP 200)

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `thread_id` | string | Luôn có — là thread dùng cho lượt này (do client gửi hoặc do server sinh). |
| `state` | object (JSON) | State đầu ra của graph sau lượt invoke; cấu trúc phụ thuộc định nghĩa graph hiện tại (ví dụ có thể chứa khóa `text` và các giá trị khác do node cập nhật). |

**Lỗi:**

- **HTTP 422:** body không hợp lệ (validation Pydantic), ví dụ `message` rỗng hoặc thiếu.
- **HTTP 503:** lỗi khi chạy graph hoặc graph chưa khởi tạo; `detail` là chuỗi mô tả lỗi từ server.

---

## Endpoint: lịch sử checkpoint theo thread

| Thuộc tính | Giá trị |
|------------|---------|
| Phương thức & đường dẫn | `GET /threads/{thread_id}/history` |
| Path | `thread_id` — định danh phiên (cùng ý nghĩa với `thread_id` ở chat). |
| Body | Không |

### HistoryResponse (phản hồi thành công, HTTP 200)

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `thread_id` | string | Trùng với path. |
| `checkpoints` | mảng | Danh sách snapshot; thứ tự theo iterator LangGraph `get_state_history` (thực tế: **mới nhất trước**). |

### HistoryCheckpointItem (một phần tử trong `checkpoints`)

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `values` | object | Giá trị kênh state tại snapshot (ví dụ nội dung `text` sau các bước graph). |
| `metadata` | object | Metadata đi kèm snapshot (ví dụ bước, nguồn cập nhật — phụ thuộc runtime LangGraph). |
| `created_at` | string hoặc `null` | Thời điểm tạo snapshot (ISO-like string khi có). |
| `checkpoint_id` | string hoặc `null` | Id checkpoint hiện tại. |
| `parent_checkpoint_id` | string hoặc `null` | Id checkpoint cha (liên kết chuỗi lịch sử). |

**Lỗi:**

- **HTTP 503:** lỗi khi đọc lịch sử hoặc graph chưa khởi tạo; `detail` là chuỗi mô tả.

---

## Hành vi lưu trữ phía server (ảnh hưởng frontend)

- Khi biến môi trường **`DATABASE_URL`** được cấu hình, checkpoint được lưu qua **Postgres** (bảng do LangGraph quản lý, không nằm trong script SQL nghiệp vụ academic/CTSV).
- Khi **`DATABASE_URL`** không có, server dùng **bộ nhớ trong process** — phù hợp dev; **không** giữ dữ liệu sau khi restart process.

Frontend cần hiểu: **tính bền của thread** phụ thuộc triển khai backend (Postgres vs in-memory), không phụ thuộc vào client.

---

## Phiên bản graph (ảnh hưởng nội dung `state` / `values`)

Graph hiện tại là stub (state có trường `text` và luồng xử lý cố định). Khi graph được thay bằng agent LLM hoặc thêm trường state, **hình dạng** `state` và `values` trong lịch sử có thể thay đổi; contract HTTP (path, tên trường request/response envelope) có thể giữ nguyên nếu backend không đổi version API.
