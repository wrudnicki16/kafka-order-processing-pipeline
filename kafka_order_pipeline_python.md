# Kafka Order Processing Pipeline (Python)

Hands-on repo to solidify Kafka fundamentals: topics, partitions, producers, consumer groups, offsets, and retention.

---

## 🧪 How to run

1. **Start Kafka**
   ```bash
   docker compose up -d
   ```

2. **Install deps** (in your local venv)
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run producer**
   ```bash
   KAFKA_BOOTSTRAP=localhost:9092 python src/order_generator.py
   ```

4. **Run one consumer**
   ```bash
   GROUP_ID=order-processor python src/order_processor.py
   ```

5. **Scale consumers to see partition rebalancing**
   - Open a **second terminal** and run the consumer again (same `GROUP_ID`).
   - Watch logs: each consumer will receive a disjoint subset of partitions.

6. **Test offsets (restarts)**
   - Stop one consumer (Ctrl+C), then start it again.
   - Verify it resumes from the last committed offset.

---

## 🧠 What this teaches (map to core concepts)

- **Topic & partitions:** `ensure_topic()` creates `orders` with 3 partitions → see parallelism & ordering guarantees per partition.
- **Producer acks & metadata:** `send_and_wait()` returns partition & offset → visibility into delivery.
- **Key-based partitioning:** Using `user_id` as key keeps per-user order across partitions.
- **Consumer groups:** Multiple consumers with the same `GROUP_ID` share the work (no duplicates across group).
- **Offsets & durability:** Auto-commit demo + restart semantics.
- **Retention:** Configure at broker or topic level to see messages expire.

---

## 🧪 Optional Experiments (Stretch Goals)

### A. Dead-letter queue (DLQ)
- Add a second topic `orders.dlq`.
- On DB failure or validation error, publish the original event to DLQ.

### B. Manual commits (exactly-once-ish semantics demo)
- Set `enable_auto_commit=False` and commit **after** DB insert to avoid at-least-once duplicates.

### C. Tweak retention **per topic**
- From inside the container, run:
  ```bash
  docker exec -it kafka bash
  kafka-configs.sh --bootstrap-server localhost:9092 --alter --entity-type topics --entity-name orders --add-config retention.ms=60000
  ```
  Observe that messages older than 60s are eventually deleted.

### D. Consumer groups vs. fan-out
- Start another consumer **with a different** `GROUP_ID` (e.g., `order-analytics`).
- Both groups read the **same** messages independently (pub/sub behavior).