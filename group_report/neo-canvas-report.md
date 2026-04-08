# Báo cáo nhóm — AI Product Canvas (Vietnam Airlines NEO)

**Tên nhóm:** C401 - D5

**Thành viên:**

- Đào Phước Thịnh — 2A202600029
- Nguyễn Tri Nhân — 2A202600224
- Trần Xuân Trường — 2A202600321
- Hồ Sỹ Minh Hà — 2A202600060
- Nông Nguyễn Thành — 2A202600250
- Đào Văn Công — 2A202600031

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | **User:** Hành khách Vietnam Airlines cần tra cứu chuyến bay, giá vé, hành lý, quy định bay.<br>**Pain:** Tra cứu động yếu (ví dụ giá vé dịp lễ); bot im lặng khi xử lý lâu; chờ tổng đài quá tải.<br>**AI:** Phản hồi 24/7; clarify để đủ entity (thời gian, điểm đi/đến) rồi gọi API tra vé — không dừng ở FAQ tĩnh. | **Ảnh hưởng khi sai:** Bối rối, spam “Gặp tư vấn viên”, rủi ro tài chính nếu tin thông tin sai (giá vé, quy định pháp lý). **Biết AI đang làm gì / có thể sai:** Ưu tiên precision; “showing work” (ví dụ “đang tổng hợp thông tin…”). **User sửa / thoát an toàn:** Thông báo rõ khi chuyển người (ví dụ “⚠️ Đã kết nối với tư vấn viên”), nút “Quay lại chat với NEO”, fallback tư vấn viên khi độ tin thấp hoặc câu hỏi ngoài phạm vi. | **Cost:** Ước tính ~$0.01–$0.02/request (LLM intent + entity).<br>**Latency:** Mục tiêu dưới 3 giây; tác vụ API nặng thì hiển thị trạng thái chờ.<br>**Risk:** Hallucination (hậu quả pháp lý, tham chiếu case hàng không); lỗi API thời gian thực khiến bot treo cục bộ. |

---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp  
☑ Augmentation — AI gợi ý, user quyết định cuối cùng  

**Justify:** Thông tin hàng không gắn tài chính và lịch trình. Automation hoàn toàn nếu sai (hành lý, hoàn vé…) rủi ro uy tín và pháp lý lớn. AI tư vấn, làm rõ ý định và hỗ trợ tra cứu; dưới ngưỡng tin cậy (ví dụ ~60%) hoặc yêu cầu phức tạp thì **fallback** ngay sang tư vấn viên.

Gợi ý: nếu AI sai mà user không biết → automation nguy hiểm, cân nhắc augmentation.

---

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Log để tinh chỉnh prompt / system message. Phiên phải spam “Gặp tư vấn viên” → gắn nhãn friction point để ưu tiên sửa. |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | Resolution rate; handoff frequency; drop-off rate khi bot trả văn bản quá dài. |
| 3 | Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___ | ☑ User-specific (PNR, lịch sử bay) · ☑ Domain-specific (quy định nội bộ VNA) · ☑ Real-time (giá vé, trạng thái chuyến từ API) · ☐ Human-judgment · ☐ Khác |

**Có marginal value không?** (Model đã biết cái này chưa? Ai khác cũng thu được data này không?)

Có. Log và ca handoff bot ↔ tư vấn viên giúp xây RAG trên tình huống thật mà LLM chung không có — moat dịch vụ khách hàng cho VNA.

---

## Cách dùng

1. Điền Value trước — chưa rõ pain thì chưa điền Trust/Feasibility  
2. Trust: trả lời 4 câu UX (đúng → sai → không chắc → user sửa)  
3. Feasibility: ước lượng cost, không cần chính xác — order of magnitude đủ  
4. Learning signal: nghĩ về vòng lặp dài hạn, không chỉ demo ngày mai  
5. Đánh [?] cho chỗ chưa biết — Canvas là hypothesis, không phải đáp án  

---

*AI Product Canvas — Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*
