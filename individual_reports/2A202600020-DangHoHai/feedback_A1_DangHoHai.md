# Feedback — Demo Round Day 6
**Người đánh giá:** Đặng Hồ Hải - 2A202600020  
**Nhóm:** VinUni_A1

---

## Nhóm VinUni_X100: AI Tra cứu học tập cho phụ huynh
| Tiêu chí | Điểm |
|----------|------|
| Problem-solution fit | 5 |
| AI product thinking | 4 |
| Demo quality | 4 |

**Điều làm tốt:**  
Sản phẩm đánh trúng nhu cầu thực tế. Hệ thống hoạt động trơn chu, tập trung vào dữ liệu nội bộ, ít lan man. Nhóm có suy nghĩ ra failure modes, tư duy rủi ro khá tốt

**Gợi ý cải thiện:**  
Cân nhắc handle bài toán "identity mapping". Nếu phụ huynh có nhiều con theo học thì cần 1 lớp middleware để quản lý profile. Cần siết chặt hơn về phân quyền để đảm bảo không rò rỉ thông tin

---

## Nhóm VinUni_B2: Tra cứu quy định và thông tin học vụ
| Tiêu chí | Điểm |
|----------|------|
| Problem-solution fit | 4 |
| AI product thinking | 3 |
| Demo quality | 4 |

**Điều làm tốt:**  
Tốc độ phản hồi khá ổn. Từ chối các câu hỏi ngoài phạm vi tốt -> Sử dụng prompt engineering kỹ lưỡng để kiểm soát hành vi model


**Gợi ý cải thiện:**  
Cần có cơ chế Fallback mượt mà hơn khi dữ liệu tìm kiếm không đủ độ tin cậy.

---

## Nhóm VinUni_F1
| Tiêu chí | Điểm |
|----------|------|
| Problem-solution fit | 4 |
| AI product thinking | 4 |
| Demo quality | 3 |

**Điều làm tốt:**  
Thiết kế Workflow với nhiều role khác nhau, xử lý được nhiều tình huống hỗ trợ học tập. Demo cho thấy khả năng suy luận logic khá ổn trong các tác vụ thông thường.

**Gợi ý cải thiện:**  
Với question phức tạp yêu cầu truy vấn nhiều bước (>10 bước) khác nhau system bị out-of-context hoặc timeout -> Hallucination. Nên áp dụng kỹ thuật chain-of-thought

---

## Tổng kết
Nhìn chung các nhóm đều xác định được bài toán thực tế và có hướng triển khai rõ ràng. Các giải pháp đã bắt đầu chú trọng hơn đến trải nghiệm người dùng cuối thay vì chỉ tập trung vào công nghệ thuần túy. Tuy nhiên, một số nhóm cần cân nhắc về việc bảo mật và trải nghiệm người dùng khi hệ thống scale lớn.
