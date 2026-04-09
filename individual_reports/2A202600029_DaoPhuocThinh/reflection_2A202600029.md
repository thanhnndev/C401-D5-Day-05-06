# Individual reflection — Đào Phước Thịnh (2A202600029)

## 1. Role
**Ideator (Khởi tạo ý tưởng) + Lead Tool Engineer**. Chịu trách nhiệm định hình luồng nghiệp vụ của StudentOps AI, xác định các tool cần thiết kế cho team và trực tiếp xây dựng hệ thống Tools cho Use Case 1 (Truy vấn dữ liệu).

## 2. Đóng góp cụ thể
- **Định hình dự án:** Đề xuất ý tưởng "StudentOps AI" tập trung vào nỗi đau (painpoint) của Phòng Đào tạo và CTSV tại VinUni trong việc lọc dữ liệu sinh viên phức tạp.
- **Thiết kế & Xây dựng Tool UC1:** Phát triển bộ công cụ `get_db_schema_tool` và `execute_query_tool`. Đặc biệt là tối ưu hóa kiến trúc tool từ dạng đơn lẻ cho từng DB sang dạng **Generic Tool** (nhận tham số `db_type`), giúp Agent linh hoạt hơn khi mở rộng hệ thống.
- **Thiết lập Guardrails:** Trực tiếp cài đặt cơ chế bảo mật **Read-only** nghiêm ngặt cho `sql_query_tool`, sử dụng Regex để chặn các lệnh gây nguy hiểm như `DELETE`, `DROP`, `UPDATE`, đảm bảo an toàn cho dữ liệu sinh viên.
- **Phân chia Tooling:** Thiết kế interface và logic cho các tool còn lại (UC2 - Email drafting) để các thành viên khác trong team triển khai đồng bộ.

## 3. SPEC mạnh/yếu
- **Mạnh nhất: 4 Paths (UX) & Guardrails.** Bản SPEC đã lường trước rất kỹ các lỗi của AI (NL-to-SQL sai, hallucinate email) và đưa ra cơ chế phòng thủ đa lớp: Hiển thị query mô tả cho user xác nhận + HIL (Human-in-the-loop) bắt buộc trước khi gửi email.
- **Yếu nhất: ROI (Kịch bản tài chính).** Các con số giả định về thời gian tiết kiệm (3-4h/ngày) còn mang tính lý tưởng. Cần bổ sung thêm phần tính toán chi phí token thực tế khi Agent phải quét schema liên tục đối với các DB có hàng trăm bảng.

## 4. Đóng góp khác
- **Kiểm thử Tool:** Viết script `test_tools_manual.py` để team có thể tự kiểm tra kết nối Database và độ nhạy của Guardrails trước khi tích hợp vào Agent chính.
- **Hỗ trợ Team:** Hướng dẫn các thành viên cách bind tool vào model và cách xử lý lỗi `psycopg` trên môi trường Windows.

## 5. Điều học được
Qua dự án này, tôi nhận ra rằng việc thiết kế Tool cho Agent không chỉ là viết hàm logic thông thường. Điểm mấu chốt là **"AI-friendly Interface"**: Tool phải trả về dữ liệu thô nhưng súc tích, và quan trọng nhất là phải có **Constraint (Ràng buộc)** ngay tại level code để bù đắp cho sự thiếu ổn định của LLM trong các thao tác dữ liệu nhạy cảm.

## 6. Nếu làm lại
Tôi sẽ tập trung vào việc hiện thực hóa **Few-shot Prompting** cho các query SQL phức tạp ngay từ đầu. Trong quá trình làm, tôi nhận thấy LLM đôi khi nhầm lẫn giữa các bảng có tên tương tự nhau, nếu có bộ ví dụ (Sample queries) đi kèm trong Tool, độ chính xác của UC1 sẽ cao hơn nhiều.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI (Antigravity/Gemini) hỗ trợ cực tốt trong việc viết code Boilerplate cho các tool kết nối Postgres và brainstorm ra các trường hợp Failure modes mà con người dễ bỏ sót (như SQL Injection qua ngôn ngữ tự nhiên).
- **Sai/mislead:** Khi yêu cầu tối ưu hóa tool, AI đôi khi đề xuất các giải pháp trang trí (thêm header, format bảng cầu kỳ) khiến kết quả trả về quá dài dòng, làm Agent bị loãng thông tin. Tôi phải điều chỉnh lại để giữ định dạng return "sạch" nhất cho Agent xử lý.
