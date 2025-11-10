import asyncio
import json
import os
import random
import string
import time
from aiokafka import AIOKafkaProducer
from common import ensure_topic, KAFKA_BOOTSTRAP, TOPIC

INTERVAL = float(os.getenv("INTERVAL", "0.5"))  # seconds

# Simple random data helpers

def rand_id(prefix: str) -> str:
    return prefix + '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

async def main():
    await ensure_topic()

    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP,
                                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                                key_serializer=lambda v: v.encode("utf-8") if v else None)
    await producer.start()
    print(f"[producer] sending to topic={TOPIC} @ {KAFKA_BOOTSTRAP}")

    try:
        i = 0
        while True:
            order_id = rand_id("ord")
            user_id = f"user_{random.randint(1, 6)}"  # small range to see partitioning by key in stretch goal
            payload = {
                "order_id": order_id,
                "user_id": user_id,
                "amount": round(random.uniform(5, 250), 2),
                "ts": time.time(),
            }
            # Partitioning hint: set key to user_id to achieve stable ordering per user
            md = await producer.send_and_wait(TOPIC, value=payload, key=user_id)
            print(f"[producer] sent {payload['order_id']} -> partition={md.partition} offset={md.offset}")
            i += 1
            await asyncio.sleep(INTERVAL)
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())