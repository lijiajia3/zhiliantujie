#!/bin/bash

# 进入后端目录（如果你放在 hr-api 下）
cd hr-api

# 激活虚拟环境（根据你实际路径）
source ../venv/bin/activate

# 读取 .env 文件
export $(grep -v '^#' ../.env | xargs)

# 启动 FastAPI
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
