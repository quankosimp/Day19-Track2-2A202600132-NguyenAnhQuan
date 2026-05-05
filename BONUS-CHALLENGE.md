# Bonus Challenge — Build Your Own AI Memory

> English version: [`BONUS-CHALLENGE-EN.md`](BONUS-CHALLENGE-EN.md)

**Loại:** Brainstorming + creative session — tách khỏi lab chính, hoàn toàn tự nguyện.
**Đối tượng:** Bạn vào vai *AI engineer thiết kế hệ thống memory* cho 1 trợ lý cá nhân.
**Effort target:** 4–6 giờ tập trung. Khuyến khích pair (2–3 người), brainstorm trước, code sau.
**Vibe coding khuyến khích:** code boilerplate AI lo, *architecture decisions* bạn tự nghĩ + viết.

Bonus dành cho học viên muốn vượt qua rote deliverable và xây dựng thứ
*creative + showcase-able*. **Không có điểm số chính thức** (20 pts bonus
optional trên `rubric.md`); phần thưởng thực sự là feedback bằng văn bản từ
giảng viên về *judgment* của bạn, và 1 portfolio piece.

---

## Đề bài

Bạn đang xây 1 **trợ lý AI cá nhân cho người dùng Việt Nam** (think: ChatGPT
+ NotebookLM cho cá nhân, tiếng Việt). Trợ lý phải *nhớ*:

- **Episodic memory** — các cuộc hội thoại, tài liệu user đã đọc, ghi chú user
  tự lưu. Càng nhiều → tìm kiếm phải càng thông minh. → **Vector Store**
  (lab 19 §1–§3).
- **Stable user profile** — ngôn ngữ ưu tiên (vi/en/mix), tốc độ đọc,
  lĩnh vực quan tâm (cloud / AI / pháp luật / y tế / ...), thời gian active
  trong ngày. → **Feature Store** (lab 19 §4).
- **Recent activity** — câu query 1 giờ qua, topic đã hỏi nhiều, có pattern
  mệt mỏi (queries dài hơn về đêm) không. → **Streaming feature view**
  (lab 19 §6 streaming pipeline).

Nhiệm vụ: **thiết kế và build 1 minimal POC kết hợp cả 2**. Document is the
primary deliverable; code chỉ cần minimal để demo design quyết định.

---

## Deliverables (cho thư mục `bonus/` trong repo của bạn)

### 1. `bonus/ARCHITECTURE.md` (chính, ~600–1000 từ)

Phải có:

- **Sơ đồ kiến trúc** (ascii-art / Mermaid / hình vẽ scan tay đều OK).
  Phải show: data flow giữa episodic memory (vector) và stable profile
  (feature store), và LLM final response.

- **3 quyết định kiến trúc với tradeoff explicit:**
  1. **Chunking strategy** — episodic memory chunk thế nào? Per-message?
     Per-conversation? Semantic break? Số token? Bao gồm tradeoff về
     *retrieval quality vs storage cost vs context window*.
  2. **Feature schema** — user profile cần features gì? Mỗi feature
     entity/ttl/source là gì? Pattern: tabular features (đơn giản) vs
     embedding features (latent prefs từ history)? Bao gồm 1 lý do tại sao
     chọn pattern đó.
  3. **Freshness strategy** — khi user vừa đọc xong 1 tài liệu mới, bao lâu
     thì recall query "trợ lý nhớ gì về tôi?" phản ánh tài liệu đó?
     Sub-second (streaming Push API) vs 5-min (batch refresh) vs daily?
     Cho 3 use cases khác nhau.

- **Loại bỏ tỉ thiệu 1 lựa chọn sai với lý do** — kiểu "Tôi xem xét X nhưng
  chọn Y vì Z". Ví dụ: "Tôi xem xét lưu episodic trong feature store
  (như embedding feature view) nhưng tách riêng vào vector store vì
  re-index cycle khác hẳn (memory mới mỗi giờ vs profile theo tuần)".

- **Vietnamese-context considerations** — gì cần lưu ý cho user VN cụ thể?
  Code-switching (vi/en mix), phonetic typo, NLP tokenizer choice (pyvi
  / underthesea / whitespace split tradeoff)?

### 2. `bonus/agent.py` (~80–150 dòng)

Một agent class với 2 method tối thiểu:

```python
class HybridMemoryAgent:
    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Add a new piece of episodic memory for this user."""
        # Chunk text → embed → upsert to user-specific Qdrant collection (or filtered)

    def recall(self, query: str, user_id: str = "u_001") -> str:
        """Retrieve top-K memories + user profile features → return assembled context."""
        # 1. Get user profile + recent activity from Feast online store
        # 2. Hybrid search Qdrant filtered by user_id
        # 3. Assemble context string: "User likes <topic_affinity> reading at <speed>wpm.
        #    Recent activity: <queries_last_hour>. Top memories: <top-3>"
        # (Không cần gọi LLM thật — chỉ cần return context string)
```

Vibe code thoải mái phần này — mechanical, follow patterns từ NB2 + NB4.
Don't optimize tốc độ; optimize *clarity*.

### 3. `bonus/demo.py` (5-query script)

Chạy 5 queries minh hoạ:

1. Hỏi đơn giản (chỉ vector hit): "Tôi đã đọc gì về Kubernetes?"
2. Hỏi cần profile context: "Recommend đọc gì tiếp" (cần `topic_affinity`)
3. Hỏi cần fresh activity: "Tôi đang quan tâm gì gần đây?" (cần `queries_last_hour`)
4. Hỏi paraphrase (vector wins): "Tài liệu về tự động mở rộng hạ tầng?"
5. Hỏi mixed (hybrid + profile): "Cho tôi summary cloud security" (cần
   episodic + profile)

Output: print context được assembled cho mỗi query.

---

## Self-checklist cho strong submissions

- [ ] Sơ đồ kiến trúc rõ — không cần đẹp, cần đúng.
- [ ] 3 quyết định mỗi cái có **tradeoff explicit** (X vs Y, why X) — không
      phải "X tốt".
- [ ] Ít nhất 1 quyết định show *Vietnamese-context awareness* (token,
      code-switching, hoặc privacy/Decree-13).
- [ ] Code chạy được — `python bonus/demo.py` exits 0.
- [ ] Architecture quyết định có sự **liên kết rõ với lab concept** (PIT
      join, TTL, streaming, RRF — không bỏ pass nào).
- [ ] Honest limitations — viết 1 đoạn "What this POC doesn't handle yet"
      (ví dụ: privacy isolation per user, encryption at rest, CRUD on
      memories, multi-device sync).

---

## Format chấp nhận

- **Pair / triple work khuyến khích** — chú thích contributors trong
  `bonus/ARCHITECTURE.md` đầu file.
- Vibe coding workflow log — nếu bạn dùng AI heavily, optional ghi
  ngắn (~100 từ) "1 prompt nào hiệu quả nhất, 1 prompt nào fail" trong
  bottom của ARCHITECTURE.md. Đây không bị trừ điểm — instructor reward
  judgment, không reward "viết tay từng dòng".

## Submission

Add folder `bonus/` vào repo public của bạn (cùng repo Lab 19 chính).
Trong `submission/REFLECTION.md`, mention bạn đã làm bonus. Grader sẽ tự
review từ cùng URL public LMS.

---

## Trạng thái hoàn thành (repo hiện tại)

- [x] `bonus/ARCHITECTURE.md` đã tạo (>= 600 từ, có Mermaid architecture diagram).
- [x] Có 3 quyết định kiến trúc với tradeoff explicit (chunking, feature schema, freshness).
- [x] Có Vietnamese-context considerations (code-switching, typo, privacy context).
- [x] Có rejected alternative nêu rõ lý do.
- [x] `bonus/agent.py` có `HybridMemoryAgent.remember()` và `.recall()`.
- [x] `bonus/demo.py` chạy được với 5 query outputs (đã verify bằng `.venv/bin/python bonus/demo.py`).

---

## Topics gợi ý để mở rộng (optional, không bắt buộc)

Nếu hoàn thành 3 deliverables nhanh và muốn push xa hơn:

- **Multi-user privacy isolation** — sao mỗi user chỉ thấy memory của
  riêng mình? Qdrant filtered by user_id payload? Per-user collection?
  Encryption per-user? Tradeoff?
- **Memory decay / forgetting** — episodic memory có TTL không? Cohort-based
  pruning? "User chưa truy cập memory này 30 ngày → archive"?
- **Personalization re-ranking** — sau khi vector search trả top-50, re-rank
  bằng feature store (boost docs về topic_affinity của user)? Có thể là
  RRF với 3 retrievers thay vì 2.
- **Memory consolidation** — gộp 5 memories tương tự thành 1 summary mỗi
  tuần (LLM-driven)? Khi nào trigger?

Nhớ: không phải làm hết. **Một quyết định tốt + 1 POC chạy được** > 5 ý
tưởng dở dang.
