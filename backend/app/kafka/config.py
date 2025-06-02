import os
from enum import Enum

class KafkaConfig(Enum):    
    # ON = True if os.getenv('KAFKA_ON', 'True').lower() == 'true' else False  # When you want Kakfa
    ON = True if os.getenv('KAFKA_ON', 'False').lower() == 'true' else False  # When you don't want Kakfa
    TOPIC = os.getenv('KAFKA_TOPIC', 'my-topic')  # Replace it to yours
    BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')  # Replace it to yours
    GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'my-group')  # Replace it to yours