import asyncio
import json
import os
import sqlite3
from aiokafka import AIOKafkaConsumer
from common import ensure_topic, KAFKA_BOOTSTRAP, TOPIC

GROUP_ID = os.getenv("GROUP_ID", "order-processor")
AUTO_OFFSET_RESET = os.getenv("AUTO_OFFSET_RESET", "earliest")  # earliest|latest
DB_PATH = os.getenv("DB_PATH", "./processed.sqlite3")

# Simple SQLite persistence for processed order_ids

def init_db(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS processed (order_id TEXT PRIMARY KEY, user_id TEXT, amount REAL, ts REAL)")
    conn.commit()
    return conn

async def main():
    await ensure_topic()
    conn = init_db(DB_PATH)

    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset=AUTO_OFFSET_RESET,
        enable_auto_commit=True,  # let Kafka commit at intervals
        # For demo visibility; tune as you like
        max_poll_records=50,
    )

    await consumer.start()
    print(f"[consumer:{GROUP_ID}] listening on topic={TOPIC} @ {KAFKA_BOOTSTRAP}")
    try:
        async for msg in consumer:
            value = msg.value
            order_id = value.get("order_id")
            print(
                f"[consumer:{GROUP_ID}] partition={msg.partition} offset={msg.offset} key={msg.key.decode('utf-8') if msg.key else None} order_id={order_id} amount={value.get('amount')}"
            )
            try:
                with conn:
                    conn.execute(
                        "INSERT OR IGNORE INTO processed(order_id, user_id, amount, ts) VALUES (?,?,?,?)",
                        (order_id, value.get("user_id"), value.get("amount"), value.get("ts")),
                    )
            except Exception as e:
                print(f"[consumer:{GROUP_ID}] db error: {e}")
    finally:
        await consumer.stop()
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())