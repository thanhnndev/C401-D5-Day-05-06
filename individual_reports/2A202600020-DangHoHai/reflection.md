# Individual reflection — [Đặng Hồ Hải] ([2A202600020])

Ngày nộp: [2026-09-04]

---

## 1. Vai trò (Role)
Vai trò chính: thiết kế và triển khai tool `export_data` (`src/tools/export_data_tool.py`) để xuất báo cáo CSV/XLSX phục vụ demo và workflow export.

---

## 2. Đóng góp cụ thể (What I built / delivered)
- export_data tool: nhận `list[dict]`/`pandas.DataFrame`, xuất `.csv` (utf-8-sig) hoặc `.xlsx`, tự tạo thư mục `exports/`, trả về đường dẫn file. (`src/tools/export_data_tool.py`)

- Tests cover: `tests/test_export_tool.py` — kiểm tra export CSV, export Excel, dữ liệu rỗng và fallback format.

---

## 3. Các edge-cases đã xử lý test
- Mạnh: simple, reliable cho demo; đóng gói `@tool` dễ tích hợp với agents; xử lý encoding để hiển thị tiếng Việt trên Excel.
- Yếu: chưa hỗ trợ streaming/BytesIO cho môi trường serverless, thiếu audit/log export (ai export, filters), chưa có tùy chọn ordering/mapping cột.

---

## 4. Đóng góp khác (ngoài mục 2)
- Chuẩn hoá tên file với timestamp để tránh ghi đè; xử lý edge-case IO và trả về lỗi rõ ràng cho debug.  
- Hỗ trợ đồng đội test nhanh tính năng export trong demo và điều chỉnh mock data để kiểm tra tiếng Việt.

---

## 5. Một điều học được (trước đó chưa rõ)  
- Encoding và compatibility (Excel trên Windows) thường gây lỗi lặng lẽ; một dòng `utf-8-sig` cho CSV có thể cứu demo khỏi lỗi hiển thị tiếng Việt.
- Tự động hóa test case với pytest

--- 

## 6. Nếu làm lại, sẽ đổi gì? (Cụ thể)  
- Thêm parameter `columns`/`headers` để định nghĩa thứ tự và label cột.  
- Ghi audit log (DB) khi export thành công: `user_id`, `filters`, `path`.  
- Hỗ trợ streaming/chunking cho dataset lớn.

---

7. AI giúp gì / AI sai (mislead) ở đâu?  
- Giúp: đề xuất test cases, template code nhanh, gợi ý format/encoding và các cải tiến khả thi.  
- Sai/mislead: đôi khi đề xuất quá phức tạp (streaming + chunking) vượt scope hackathon; một số snippet cần điều chỉnh tương thích với phiên bản `pandas`/`openpyxl` trong môi trường.
