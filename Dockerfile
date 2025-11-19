# 第一阶段：构建依赖
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖（可选，根据实际需要）
RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 第二阶段：运行镜像
FROM python:3.11-slim

WORKDIR /app

# 将 builder 安装的依赖复制到最终镜像
COPY --from=builder /root/.local /root/.local

# 让 Python 能找到 user 安装路径的包
ENV PATH=/root/.local/bin:$PATH

COPY ./app ./app

EXPOSE 8000

# 使用 gunicorn + uvicorn workers 作为生产模式
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2"]