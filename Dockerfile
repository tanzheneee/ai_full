# 第一阶段：构建依赖
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 第二阶段：运行镜像
FROM python:3.11-slim

WORKDIR /app

ARG APP_DIR=/app
ENV APP_HOME=${APP_DIR}

# 创建一个非特权用户 'appuser'
# 🔑 关键：指定 UID 和 GID 为 1000，以匹配宿主机上的 'ubuntu' 用户 (最常见情况)
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID appuser && useradd -r -u $USER_ID -g appuser appuser

# 拷贝依赖
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制整个项目（你的 main.py 在根目录）
COPY . .

# 更改应用目录及其所有内容的拥有者为新创建的非特权用户
# 这确保了 'appuser' 可以读写配置文件和代码
RUN chown -R appuser:appuser $APP_HOME

USER appuser

# 创建日志目录，确保 Filebeat 有权限访问
RUN mkdir -p /home/ubuntu/logs/ai_full && chmod -R 777 /home/ubuntu/logs/ai_full

EXPOSE 8000

# 使用 gunicorn + uvicorn worker 运行 FastAPI
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2"]