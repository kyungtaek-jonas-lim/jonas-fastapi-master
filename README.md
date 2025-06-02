# Project Name
### *`jonas-fastapi-master`*

## Author
- **KyungTaek Lim (Jonas Lim)**
- Software Engineer
- **Email:** kyungtaekjonaslim@gmail.com
- **LinkedIn:** [KyungTaek Jonas Lim](https://www.linkedin.com/in/kyungtaek-jonas-lim)
- **GitHub:** [kyungtaek-jonas-lim](https://github.com/kyungtaek-jonas-lim)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)

## Introduction
Handy components on AWS (ECS, ECR)

## Features
- [Async](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/async_routes_v1.py)
- [Scheduler](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/scheduler.py)
  - `apscheduler`
    - MIT License
- [File](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/file_routes_v1.py)
  - `boto3` (S3)
    - Apache License 2.0
  - `pandas` (TO-BE)
    - BSD 3-Clause License
  - `openpyxl` (TO-BE)
    - MIT License
- Database (ORM) (TO-BE)
  - `boto3` (Secrets Manager)
    - Apache License 2.0
  - `sqlalchemy`
    - MIT License
- [Redis](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/redis_routes_v1.py)
  - `redis`
    - BSD 3-Clause License
- [JWT](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/jwt_routes_v1.py)
  - `python-jose`
    - MIT License
- [MongoDB](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/mongodb_routes_v1.py)
  - `motor` (3.6.1)
    - Apache License 2.0
- [Websocket](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/websocket_routes_v1.py)
  - `websockets`
    - MIT License
- [Cryptography (SHA256, Bcrypt, AES256, RS256)](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/cryptography_routes_v1.py)
  - `cryptography`
    - Apache License 2.0
  - `bcrypt`
    - Apache License 2.0
  - (TO-BE)
    - RSA, HMAC, SHA3-256, Argon2, ECDSA
- [Kafka](https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master/blob/main/backend/app/routes/v1/routes/kafka_routes_v1.py)
  - `aiokafka`
    - Apache License 2.0

## Installation
Follow these instructions to set up your development environment.
  - rename `Dockerfile-sample` to `Dockerfile`
  - rename `buildspec-sample.yml` to `buildspec.yml`
  - modify `AWS_ACCOUNT_ID`, `AWS_REGION`, `ECR_REPOSITORY_NAME`, `ECS_CONTAINER_NAME` in `buildspec.yml`
  - generate `RSA` keys (Without Docker Container)
    ```bash
    if [ ! -f ./keys/private.pem ]; then \
    openssl genrsa -out ./keys/private.pem 2048; \
    fi \
    && if [ ! -f ./keys/public.pem ]; then \
    openssl rsa -in ./keys/private.pem -pubout -out ./keys/public.pem; \
    fi
    ```

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master.git
   cd jonas-fastapi-master
   ```

2. **Run Kafka (Windows):**
    1. [Install](https://kafka.apache.org/downloads)

    2. Run Zookeeper
    ```bash
    .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
    ```

    3. Run Kafka Server (On a new tab)
    ```bash
    .\bin\windows\kafka-server-start.bat .\config\server.properties
    ```

    4. Create Topic (On a new tab)
    ```bash
    .\bin\windows\kafka-topics.bat --create --topic my-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ```

    5. Run Producer
    ```bash
    .\bin\windows\kafka-console-producer.bat --topic my-topic --bootstrap-server localhost:9092
    ```

    6. Run Consumer (On a new tab)
    ```bash
    .\bin\windows\kafka-console-consumer.bat --topic my-topic --from-beginning --bootstrap-server localhost:9092
    ```
  
3. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --port 8000
   # If you want Kafka, please change the value of `KafkaConfig.ON` in the file, 'backend/app/kafka/config.py'
   ```