# Reflection — Lab 19

**Tên:** Nguyễn Anh Quân
**Cohort:** _A20_
**Path đã chạy:** _lite_

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên 50 golden queries, kết quả trung bình Precision@10 là: BM25 77.8%, semantic
73.2%, hybrid 78.6% (cao nhất). Theo từng loại query: `exact` thì BM25 và hybrid
đồng hạng 96.7% (semantic 88.7%) vì từ khóa xuất hiện đúng trong corpus nên
sparse match rất mạnh. `paraphrase` thì BM25 33.3% nhỉnh hơn hybrid 32.0% và
semantic 24.0%; nguyên nhân chính là embedding `bge-small-en-v1.5` chưa tối ưu
cho paraphrase tiếng Việt. `mixed` thì hybrid thắng rõ (100.0% so với semantic
98.5% và BM25 97.0%) vì tận dụng đồng thời exact term và ngữ nghĩa.

Mình không dùng hybrid khi yêu cầu latency cực thấp và query thiên về exact
keyword (chọn BM25), hoặc khi hệ thống dùng embedding multilingual mạnh và
query chủ yếu paraphrase/ngữ nghĩa (có thể ưu tiên semantic để đơn giản pipeline).

---

## Điều ngạc nhiên nhất khi làm lab này

Hybrid không luôn thắng ở mọi slice: với `paraphrase` trong bộ dữ liệu này,
chất lượng embedding quyết định rất lớn, nên chọn model đúng ngôn ngữ quan trọng
hơn việc chỉ bật fusion.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
