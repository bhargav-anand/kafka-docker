# Kafka Data Pipeline

## Setup

- Install Docker
- Run docker-compose up
- Install Python libraries:
- Create a virtual environment: `python -m venv venv`
- Activate the environment:
- Windows: `venv\Scripts\activate`
- Linux/macOS: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Running

- Start the consumer: `python consumer.py`
- Verify processed messages:
  `docker exec -it kafka-data-pipeline-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic processed-data --from-beginning`

- Check kafka logs:
  `docker logs kafka-data-pipeline-kafka-1`

- Create topics:
  `docker exec kafka-data-pipeline-kafka-1 kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic processed-data`

- List of all the topics:
  `docker exec kafka-data-pipeline-kafka-1 kafka-topics --list --bootstrap-server localhost:9092`

- Scale up the application: Increase number of partitions and brokers

`docker exec kafka-data-pipeline-kafka-1 kafka-topics --alter --topic processed-data --partitions 3 --bootstrap-server localhost:9092`

` kafka2:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - 9093:9093
      - 29093:29093
    networks:
      - kafka-network
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: LISTENER_INTERNAL://kafka2:9093,LISTENER_EXTERNAL://localhost:29093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_INTERNAL:PLAINTEXT,LISTENER_EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 2
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1`

## Design Decisions

1. Set up a local development environment using Docker
      Docker Compose is configured to include:
         -Kafka and Zookeeper for the messaging system.
         -Data Generator container (my-python-producer) producing messages to the user-login topic.
         -Consumer Application container for processing messages.
      Ports and Networks are properly set up for communication between services.
2. Design and implement a Kafka consumer
      Kafka Consumer implemented in Python:
         -Consumes data from the user-login topic.
         -Transforms and processes data as per requirements.
         -Handles missing fields (e.g., device_type defaults to 'unknown').
         -Logs insights (e.g., popular device_type).
3. Configure another Kafka Topic and store the processed data
      Processed data is sent to the processed-data Kafka topic using the Producer.
4. Handle streaming data continuously and efficiently
      Continuous data processing in a while True loop with efficient polling.
      Handles errors such as:
         -JSON decoding errors.
         -Kafka-specific errors (e.g., network issues).
         -Default values for missing fields ensure robustness.
      Logging added for debugging and monitoring.
5. Error handling and missing fields
      Error handling is implemented:
        -Logs warnings for missing fields.
        -Logs errors for JSON decode issues and Kafka errors.
      Missing fields (device_type) are assigned default values.

## Additional Questions
1. This application can be deployed in Kubernetes cluster for production use cases. The application needs to be tested with 2x or 3x times of expected messages to identify the optimal number of partitions for each topic. The replication factor can be configured while topic creation to ensure fault tolerance. The consumer groups can be scaled dynamically based on data production if the existing consumers cant consume the whole data. We can leverage KEDA by adding it to kubernetes cluster to scale consumer group based on consumer lag.
2. The cluster can be scaled horizontally by scaling up brokers based on load on the nodes. The partitons have to reassigned subsequently to levearge the new brokers. You can provide the topics to move in a JSON file and brooker list to reassign partitions as parameters and generate a reassignment JSON file whihc can be used to reassign partitions to new brokers.

