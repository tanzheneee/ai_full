# 第一阶段：构建依赖
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .

# 💥 关键修改 1: 去掉 --user，安装到系统全局目录 (/usr/local/lib/python3.11/site-packages 和 /usr/local/bin)
# 这样所有用户都有读取和执行权限
RUN pip install --no-cache-dir -r requirements.txt

# 第二阶段：运行镜像
FROM python:3.11-slim

WORKDIR /app

ARG APP_DIR=/app
ENV APP_HOME=${APP_DIR}

# 创建一个非特权用户 'appuser'
# 🔑 关键：指定 UID 和 GID 为 1000，以匹配宿主机上的 'ubuntu' 用户
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID appuser && useradd -r -u $USER_ID -g appuser appuser

# 💥 关键修改 2: 既然在 Builder 阶段安装到了全局目录，我们需要把全局目录拷过来
# Python 全局库通常在 /usr/local/lib/python3.11/site-packages
# Python 全局可执行文件 (gunicorn) 在 /usr/local/bin
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制整个项目代码
COPY . .

# 更改应用目录及其所有内容的拥有者为新创建的非特权用户
RUN chown -R appuser:appuser $APP_HOME

# 切换用户
USER appuser

EXPOSE 8000

# 💥 关键修改 3: 直接使用全局路径的 gunicorn (或者依靠 PATH 自动寻找)
# 因为 /usr/local/bin 默认在 PATH 里，直接写 gunicorn 即可
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2"]