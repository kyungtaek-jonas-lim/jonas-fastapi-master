# Project Name

`jonas-fastapi-master` Handy components on AWS (ECS, ECR)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)

## Introduction

Handy components on AWS (ECS, ECR)

## Features

- Async
- Scheduler
  - `apscheduler`
    - MIT License
- File
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
- Redis
  - `redis`
    - BSD 3-Clause License
- JWT
  - `python-jose`
    - MIT License
- Websocket
  - `websockets`
    - MIT License

## Installation

Follow these instructions to set up your development environment.
  - rename `Dockerfile-sample` to `Dockerfile`
  - rename `buildspec-sample.yml` to `buildspec.yml`
  - modify `AWS_ACCOUNT_ID`, `AWS_REGION`, `ECR_REPOSITORY_NAME`, `ECS_CONTAINER_NAME` in `buildspec.yml`
  - generate `RSA` keys 
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
