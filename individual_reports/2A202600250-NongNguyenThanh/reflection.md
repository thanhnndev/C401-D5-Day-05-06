
# Individual reflection — Nông Nguyễn Thành (2A202600250)

## 1. Role
DevOps / nền tảng & hỗ trợ kỹ thuật: quản lý Git và luồng làm việc repo, dựng hạ tầng mail (SMTP), database (local + VPS), đồng thời hỗ trợ team hoàn thiện Frontend và Agent — phần lớn thời gian “vibecoding” cùng AI để ship nhanh trong deadline hackathon.

## 2. Đóng góp cụ thể (2–3 output rõ ràng)
- **Git & codebase:** Quản lý dự án trên Git, hỗ trợ các bạn dùng Git (branch, merge, conflict cơ bản); khởi tạo project và refactor cấu trúc thư mục/luồng import để team clone là chạy được, giảm ma sát khi nhiều người cùng commit.
- **Email:** Khởi tạo cấu hình SMTP, dựng mail server (hoặc stack gửi mail) và test gửi/nhận email để luồng UC liên quan email có môi trường ổn định trước khi gắn vào agent.
- **Database & VPS:** Tạo database, triển khai DB trên VPS và mở kết nối an toàn để app/agent connect từ môi trường dev/demo — không chỉ “có DB” mà còn giúp team biết connection string, quyền user, và kiểm tra kết nối thực tế.

## 3. SPEC mạnh/yếu
- **Mạnh nhất:** tính thực thi end-to-end (có repo, có DB, có mail test được) — phù hợp vai trì “làm cho hệ chạy được” trong thời gian ngắn.
- **Yếu nhất:** phần mô tả chi tiết bảo mật & vận hành (rotate credential, backup DB trên VPS, policy khi expose port) — hackathon thường ưu tiên demo nên dễ để lại nợ kỹ thuật nếu không ghi chú rõ cho bước sau.

## 4. Đóng góp khác (ngoài mục 2)
- Hỗ trợ hoàn thiện Frontend: chỉnh env, proxy/API base URL, và các vấn đề build khi ghép với backend.
- Hỗ trợ hoàn thiện Agents: môi trường chạy, biến môi trường, kết nối tool tới DB/mail khi tích hợp.
- **“Bảo vệ” dự án khi team khác tới hỏi:** làm rõ phạm vi demo, trả lời ở mức kiến trúc tổng quan.

## 5. Một điều học được (trước đó chưa rõ)
Trước mình nghĩ “infra là chạy server”. Sau đợt này thấy rõ: giá trị lớn nhất là **giảm thời gian chờ của cả team** — một lần cấu hình Git/DB/mail đúng, mọi người ít bị kẹt hơn cả chục lần so với mỗi người tự mò.

## 6. Nếu làm lại, sẽ đổi gì? (cụ thể)
- Viết ngắn một `SETUP.md` (hoặc mục trong README) cho: clone repo, env mẫu, lệnh migrate/seed nếu có, và checklist test SMTP + DB từ máy local.
- Khóa sớm quy ước nhánh Git (ví dụ `main`/`develop`/feature) và template PR mô tả để giảm merge conflict khi sát deadline.
- Chuẩn bị sẵn “câu trả lời mẫu” khi team ngoài hỏi: kiến trúc + demo, phần nào không share.

## 7. AI giúp gì / AI sai (mislead) ở đâu?
- **Giúp:** hỗ trợ setup, coding, hoàn thiện tính năng, viết script, làm việc với database… — giai đoạn boilerplate và lặp lại nhiều thì AI đẩy nhanh rõ rệt.
- **Sai/mislead:** đôi khi AI đi quá **spec** team đã đặt ra; với demo hackathon thường chỉ cần **một** luồng/tính năng chính, trong khi AI hay “mở rộng” thêm flow hoặc module không cần thiết. Ngoài ra dễ gặp **ảo giác là mình đúng** (confidence cao nhưng sai context hoặc sai giả định môi trường) — vẫn phải tự đối chiếu spec và test thật.

---

*P.S. Vibecoding với AI giúp mình ship nhanh, nhưng phần “chạy được trên máy bạn” vẫn phải tự verify — AI không thay được bước test thật trên VPS và email thật. :)*
