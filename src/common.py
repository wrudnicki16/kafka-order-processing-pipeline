import asyncio
import os
from aiokafka import AIOKafkaAdminClient
from aiokafka.admin import NewTopic

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("TOPIC", "orders")
PARTITIONS = int(os.getenv("PARTITIONS", "3"))
REPLICATION = int(os.getenv("REPLICATION", "1"))

async def ensure_topic(topic: str = TOPIC, partitions: int = PARTITIONS, replication: int = REPLICATION) -> None:
    """Create topic if it doesn't exist. Idempotent for our use.
    """
    admin = AIOKafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP)
    await admin.start()
    try:
        existing = await admin.list_topics()
        if topic in existing:
            print(f"[admin] topic '{topic}' already exists with partitions={existing[topic].num_partitions if hasattr(existing[topic], 'num_partitions') else 'unknown'}")
            return
        new_topic = NewTopic(name=topic, num_partitions=partitions, replication_factor=replication)
        await admin.create_topics([new_topic])
        print(f"[admin] created topic '{topic}' with partitions={partitions}, replication={replication}")
    except Exception as e:
        # Kafka returns TopicAlreadyExistsError racing with other processes; safe to ignore
        print(f"[admin] ensure_topic warning: {e}")
    finally:
        await admin.close()

async def shutdown_signal(loop):
    for sig in ('SIGINT', 'SIGTERM'):
        try:
            loop.add_signal_handler(getattr(__import__('signal'), sig), loop.stop)
        except Exception:
            pass