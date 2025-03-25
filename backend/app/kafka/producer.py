from aiokafka import AIOKafkaProducer
import asyncio
import json
from app.kafka.config import KafkaConfig

producer = None

async def get_kafka_producer():
    global producer
    if producer is None:
        producer = AIOKafkaProducer(
            bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS.value,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await producer.start()
    return producer

async def send_to_kafka(topic: str, message: dict):
    kafka_producer = await get_kafka_producer()
    await kafka_producer.send_and_wait(topic, message)