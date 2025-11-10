# Kafka Order Processing Pipeline (Python)

A compact project to learn Kafka by doing. You’ll build a producer and a consumer, then observe partitions, offsets, retention, and consumer groups in action.

## Quickstart

```bash
docker compose up -d
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
KAFKA_BOOTSTRAP=localhost:9092 python src/order_generator.py
GROUP_ID=order-processor python src/order_processor.py
```

## Learning checkpoints

- Create a topic with 3 partitions and see rebalancing when adding a second consumer.
- Restart consumers and verify offset-based resume.
- Change retention and watch old messages disappear.
- Use a message key (`user_id`) to guarantee per-user ordering.

## Env vars

- `KAFKA_BOOTSTRAP` (default `localhost:9092`)
- `TOPIC` (default `orders`)
- `PARTITIONS` (default `3`)
- `REPLICATION` (default `1`)
- `GROUP_ID` for consumer
- `AUTO_OFFSET_RESET` (default `earliest`)

## Troubleshooting

- If producer/consumer can’t connect: ensure the broker is up and `ADVERTISED_LISTENERS` is `localhost:9092`.
- On macOS with Docker Desktop, avoid using `host.docker.internal` here—this compose advertises `localhost`.
- If `aiokafka` complains about metadata: wait a few seconds after `docker compose up -d` before starting clients.
```

---

## ✅ What to observe

- **Load balancing:** When you start multiple consumers in the same group, each gets a subset of partitions.
- **Ordering:** Messages from the same `user_id` arrive in order (keyed partitioning).
- **Offsets:** Restart a consumer; it resumes where it left off.
- **Retention:** After decreasing `retention.ms`, old messages vanish.

---

## 🧹 Cleanup

```bash
docker compose down -v
rm -rf .venv processed.sqlite3
```
