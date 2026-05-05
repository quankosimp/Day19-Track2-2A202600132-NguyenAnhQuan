from __future__ import annotations

from agent import HybridMemoryAgent


def main() -> int:
    agent = HybridMemoryAgent()

    # seed episodic memories
    agent.remember("Tôi đã đọc tài liệu về Kubernetes autoscaling và HPA cho hệ thống microservices.")
    agent.remember("Hôm qua tôi xem bài viết cloud security về IAM, least privilege và secret rotation.")
    agent.remember("Tôi ghi chú rằng đội backend đang dùng Redis cache và cần tối ưu TTL cho session.")
    agent.remember("Tài liệu về database sharding và replication cho workload tăng trưởng nhanh.")
    agent.remember("Bài viết tiếng Việt về tự động mở rộng hạ tầng theo lưu lượng truy cập giờ cao điểm.")

    queries = [
        "Tôi đã đọc gì về Kubernetes?",
        "Recommend đọc gì tiếp",
        "Tôi đang quan tâm gì gần đây?",
        "Tài liệu về tự động mở rộng hạ tầng?",
        "Cho tôi summary cloud security",
    ]

    for i, q in enumerate(queries, 1):
        print(f"\n=== Query {i}: {q} ===")
        print(agent.recall(q))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
