from confluent_kafka import Consumer, Producer
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Kafka Consumer
consumer = Consumer({
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest',  # start reading from the earliest message
})

# Initialize Kafka Producer
producer = Producer({'bootstrap.servers': 'localhost:29092'})

# Subscribe to the 'user-login' topic
consumer.subscribe(['user-login'])

# Process Messages
try:
    while True:
        msg = consumer.poll(1.0)  # Timeout for poll (in seconds)

        if msg is None:
            continue  # No message, continue polling
        if msg.error():
            logger.error(f"Error: {msg.error()}")
            continue

        # If a message is received successfully
        data = json.loads(msg.value().decode('utf-8'))
        logger.info(f"Received message: {data}")

        # Check if 'device_type' exists, otherwise handle the missing field
        if 'device_type' not in data:
            logger.warning("Missing 'device_type' in the message.")
            # Optionally, add a default value for 'device_type'
            data['device_type'] = 'unknown'  # You can set it to a default value or handle accordingly

        # Data Transformation Example: Add a "processed" field
        processed_data = {
            "user_id": data.get("user_id"),
            "app_version": data.get("app_version"),
            "device_type": data["device_type"],  # Now it's guaranteed to exist
            "ip": data.get("ip"),
            "locale": data.get("locale"),
            "device_id": data.get("device_id"),
            "timestamp": data.get("timestamp"),
            "processed": True
        }

        # Send the transformed message to a new topic ('processed-data')
        producer.produce('processed-data', value=json.dumps(processed_data))
        logger.info(f"Processed and sent message: {processed_data}")
        producer.flush()

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
