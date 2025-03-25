from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.kafka.config import KafkaConfig

async def consume():
    consumer = AIOKafkaConsumer(
        KafkaConfig.TOPIC.value,
        bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS.value,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id=KafkaConfig.GROUP_ID.value
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Consumed message: {msg.value}")
    finally:
        await consumer.stop()