# 第一阶段：构建依赖
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 第二阶段：运行镜像
FROM python:3.11-slim

WORKDIR /app

# 拷贝依赖
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制整个项目（你的 main.py 在根目录）
COPY . .

EXPOSE 8000

# 使用 gunicorn + uvicorn worker 运行 FastAPI
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2"]