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
- Scheduler (`apscheduler` - MIT License)

## Installation

Follow these instructions to set up your development environment.
   - rename `Dockerfile-sample` to `Dockerfile`
   - rename `buildspec-sample.yml` to `buildspec.yml`
   - modify `AWS_ACCOUNT_ID`, `AWS_REGION`, `ECR_REPOSITORY_NAME`, `ECS_CONTAINER_NAME` in `buildspec.yml`

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kyungtaek-jonas-lim/jonas-fastapi-master.git
   cd jonas-fastapi-master
