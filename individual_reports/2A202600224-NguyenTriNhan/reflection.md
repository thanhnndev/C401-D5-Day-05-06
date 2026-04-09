
# Individual reflection — Nguyễn Trí Nhân (2A202600224)

## 1. Role
Frontend/UI implementer (Next.js + Tailwind/shadcn). Phụ trách hiện thực giao diện theo flow demo và chuẩn hoá các trạng thái UI (empty/loading/error).

## 2. Đóng góp cụ thể (2–3 output rõ ràng)
- Xây UI khung chat: bố cục `ChatContainer`, bubble cho user/assistant, `TypingIndicator`, và màn hình `WelcomeScreen` để onboarding khi chưa có hội thoại.
- Làm layout điều hướng: sidebar cho app (khu vực navigation + vùng nội dung), đảm bảo dùng đúng component trong design system và dễ mở rộng thêm mục demo.
- Hoàn thiện màn hiển thị kết quả truy vấn: `SQLQueryCard` + `DataTable` để trình bày query/response rõ ràng, có state rỗng (chưa có data) và state đang tải.

## 3. SPEC mạnh/yếu
- Mạnh nhất: interaction states & consistency
	- Lúc ghép demo, mình ưu tiên “nhìn là hiểu trạng thái” (đang nhập/đang trả lời/chưa có dữ liệu). Nhờ dùng nhất quán các component (card, table, empty, skeleton/spinner) nên UI ít bị “mỗi chỗ một kiểu”, giảm thời gian chỉnh lại khi deadline sát.
- Yếu nhất: accessibility + kiểm thử responsive
	- Vì tập trung hoàn thành màn demo nhanh, mình chưa kiểm tra kỹ về UX nên sinh ra các trường hợp ko bấm được response, lệch khung chat

## 4. Đóng góp khác (ngoài mục 2)
- Support teammate ghép dữ liệu mock vào UI: chỉnh format text, spacing, và xử lý tràn nội dung (long message/long SQL) để không phá layout.
- Debug các lỗi “nhìn thấy ngay” trong demo: lệch khung chat, overflow khi scroll, và thống nhất style cho nút/label trong các khu vực khác nhau.
- QA nhanh luồng demo: đi qua các case (chưa chat, đang chat, có/không có kết quả truy vấn) để chắc chắn không có màn nào bị “trống trắng”.

## 5. Một điều học được (trước đó chưa biết)
Trước hackathon mình nghĩ “UI xong là đẹp”. Sau khi làm demo mới thấy: chất lượng sản phẩm phụ thuộc mạnh vào việc định nghĩa state rõ ràng (empty/loading/error/success). Chỉ cần thiếu 1 state là demo dễ bị rối, dù UI component nhìn vẫn ổn.

## 6. Nếu làm lại, sẽ đổi gì? (cụ thể)
- Ngay từ đầu sẽ viết checklist UI states cho từng màn (empty/loading/error/success) và tạo fixture data (1–2 bộ) để test layout sớm.
- Khóa sớm “contract” giữa UI và logic: naming props + shape dữ liệu (message/query/result) để lúc tích hợp không phải sửa lại nhiều.
- Dành 30 phút cuối mỗi ngày để test responsive (ít nhất 2 breakpoint) và thử tab/enter để kiểm tra focus/keyboard.

## 7. AI giúp gì / AI sai (mislead) ở đâu?
- Giúp:
	- Dùng AI để gợi ý bố cục Tailwind nhanh (grid/flex/spacing) và các cách xử lý overflow cho đoạn text dài trong chat và SQL.
	- Gợi ý cách tổ chức component nhỏ (message item, indicator, empty state) để dễ reuse và giảm lặp.
- Sai/mislead:
	- AI hay đề xuất thêm “nice-to-have” như animation phức tạp, notification, hoặc thêm màn/flow mới (đăng nhập, lưu lịch sử…) nhìn hấp dẫn nhưng vượt scope hackathon.
	- Có lúc AI giả định sai API của component (props/variant) khiến mình mất thời gian thử , bài học là phải đối chiếu với codebase/design system hiện có trước khi áp dụng.

