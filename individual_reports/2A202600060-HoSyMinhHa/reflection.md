# Individual reflection — Hồ Sỹ Minh Hà (2A202600060)

## 1. Role
AI developer, phụ trách phát triển kiến trúc Agent.  Problem researcher.

## 2. Đóng góp cụ thể
- Thiết kế kiến trúc LangGraph agents.
- Đóng góp ý kiến cho việc tích hợp đa cơ sở dữ liệu, cách cấu trúc tối ưu mà vẫn đảm bảo tính LLM freindliness. 
- Chọn ý tưởng ban đầu và phát triên paint point.

## 3. SPEC mạnh/yếu
- Mạnh: có tư duy phát triển hệ thống mang tính thực tế . Có nền tảng AI vững chắc để, đảm bảo không choáng ngợp trong môi trường có nhịp độ cao như hackathon.
- Yếu: kỹ năng giải quyết vấn đề còn yếu, cụ thể trong cuộc thi đã mất vài giờ stuck một vấn đề trong việc quản lý state giữa các node langgraph. Kỹ năng giải thích vấn đề còn yếu. 

## 4. Đóng góp khác
- Tham gia feedback cho các nhóm khác trong khu vực. Tập trung đánh giá problem statement, scope, định hướng, tính thực tế và demo. Đưa ra đóng góp hướng phát triển.

## 5. Insight quan trọng rút ra từ feedback 4 team
- MVP ban đầu không nhất thiết đầy đủ chức năng, code clean hay architecture cao siêu. Chỉ cần nhanh, có đủ chức năng cốt lõi đề vào thị trường vả cho người dùng thấy được lợi ích.
- Scope rất quan trọng, scope đủ nhỏ nhưng sâu luôn tốt hợn một scope lớn nhưng không có phương hướng.
- Đa số nhóm có ý tưởng hay, nhưng chỉ ở mức 'ý tưởng'. Không khai thác sâu về use case, nhu cầu, evaluation plan và định hướng lâu dài. Thiếu evaluation metrics tốt -> thiếu tầm nhìn về failure modes.
- Rất nhiều nhóm vẫn xem nhẹ về chỉ số precision và recall, hai chỉ số cự kì quan trọng trong các dự án thực tế.

## 6. Nếu làm lại
Định nghĩa metrics rõ ràng ngay từ đầu, thu thập thêm thông tin về nhu cầu sớm nhất có thể. Bắt đầu xây dựng MVP sớm hơn. Và chuẩn bị đầy đủ tài nguyên cho việc vibecode hơn, từ đó tăng tốc độ phát triển và giải quyết vấn đề.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI hỗ trợ cực tốt trong việc phân tích codebase, đặc biệt trong việc code chức năng riêng lẻ vài giải quyết bug ẩn. Đẩy nhanh tiến độ ra prototype.
- **Sai/mislead:** Dễ hallucination khi thiếu kiến thức về Framework được truy vấn. Khi một câu trả lời bị hallucination, tất cả các câu trả lời sau đều đưa ra thông tin sai lệch và không có tính nhất quán. Gần như mất luôn ngữ cảnh, tốn nhiều thời gian và tokens.
