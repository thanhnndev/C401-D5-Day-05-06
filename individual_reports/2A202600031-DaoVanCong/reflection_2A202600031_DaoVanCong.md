# Individual reflection — Đào Văn Công (2A202600031)

## 1. Role
Thiết kế tool: email_draft.py phục vụ tạo form email và tempalte html tương ứng. Tham gia viết test và code thêm tool email.py để gửi email hàng loạt.

## 2. Đóng góp cụ thể

Thiết kế tool email_draft.py theo các bước:
    
    - có các case như: sinh viên muốn truy vấn xem điểm, sinh viên nợ học phí, sinh viên đã đóng tiền. Tất cả đều có email gửi thông báo.

Thiết kế tool email.py để phục vụ gửi email hàng loạt: 
    
    - hàm *bulk_email_sender_tool()* để gửi email hàng loạt. Sau đó thống kê lại các email được gửi thành công hay thất bại.

## 3. SPEC mạnh/yếu

- Mạnh nhất: nghĩ ra được case "chi tiết" từng trường hợp vì mỗi lần thông báo email cần có 1 form giao diện khác nhau 

- Yếu nhất: gửi video hàng loạt chạy rất lâu, và cần email lấy chính xác từ tool query database trước đó.

## 4. Đóng góp khác
- Kết hợp :Chạy test với các trường hợp khác nhau, phục vụ email_logging, sau đó cần chạy lại các email gửi thất bại. 

## 5. Điều học được
Trước hackathon chỉ nghĩ failure hay metric là vấn đề chạy với dữ liệu lớn

Sau khi thiết kế: nhận ra failure hay metric còn phụ thuộc vào business logic và cách thiết lập tool, LangGraph để Agent chạy.

Failure và Metric là quyết định dựa trên business và kỹ thuật.

## 6. Nếu làm lại
Sẽ test tool email_draft sớm hơn — để có thể phân loại từng loại mail ra có form giao diện phù hợp.

Test email.py sớm hơn để có thể cấu hình mail server. Nếu test sớm từ tối D5 thì có thể kiểm thử nhiều cách gửi email nhanh hơn.

## 7. AI giúp gì / AI sai gì
- **Giúp:** dùng Gemini để brainstorm failure — nó gợi ý được cái nguy cơ
  mà nhóm không nghĩ ra. Dùng Gemini để test prompt nhanh qua AI Studio.

- **Sai/mislead:** Gemini gợi ý thêm feature "email_logging" và "xin xác thực quyền truy vấn DB 1 lần duy nhất cho các lần truy vấn sau đó".