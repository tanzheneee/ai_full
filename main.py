import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from nacos import NacosClient
from nacos import NacosException
from app.core.config import load_global_config
from app.db.session import init_db_engine
from app.routers import user_router
import time
import logging
from app.core.logger import setup_logging

# 1. 启动参数从环境变量获取
NACOS_HOST = os.environ.get('NACOS_HOST', 'localhost')
NACOS_PORT = int(os.environ.get('NACOS_PORT', 8848))

# 2. 其他 Nacos 参数
NACOS_SERVER_ADDRESSES = f"{NACOS_HOST}:{NACOS_PORT}"
NACOS_NAMESPACE = os.environ.get('NACOS_NAMESPACE', "")
NACOS_GROUP = os.environ.get('NACOS_GROUP', "DEFAULT_GROUP")
NACOS_DATA_ID = os.environ.get('NACOS_DATA_ID', "ai_app.yaml")
NACOS_USERNAME = os.environ.get('NACOS_USERNAME', "")
NACOS_PWD = os.environ.get('NACOS_PWD', "")

# 存储全局配置
APP_CONFIG = {}

# 初始化日志
setup_logging(
    app_name="ai_app",
    log_level="INFO",
    log_dir="/var/log/fastapi",
    enable_console=True,
    enable_file=True
)

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------

# FastAPI 实例
app = FastAPI()

# 2. 注册路由 (顶级作用域)
app.include_router(user_router.router)


@app.on_event("startup")
async def startup_event():
    """在应用启动时执行：连接 Nacos 并加载配置"""
    global APP_CONFIG

    print(f"Connecting to Nacos at: {NACOS_SERVER_ADDRESSES},{NACOS_NAMESPACE},{NACOS_DATA_ID},{NACOS_GROUP}")
    try:
        # 实例化 Nacos 客户端
        client = NacosClient(
            server_addresses=NACOS_SERVER_ADDRESSES,
            namespace=NACOS_NAMESPACE,
            username=NACOS_USERNAME,
            password=NACOS_PWD
        )

        # 获取配置内容 (假设是 YAML)
        config_str = client.get_config(data_id=NACOS_DATA_ID, group=NACOS_GROUP)


        # 2. 加载全局配置
        load_global_config(config_str)  # config_str 是从 Nacos 拉取的原始字符串

        # 3. 初始化数据库连接池
        init_db_engine()

        print("✅ 应用初始化成功：Nacos配置已加载，数据库引擎已创建。")

    except NacosException as e:
        print(f"❌ Nacos连接或配置加载失败: {e}")
        # 生产环境应该在这里抛出致命异常，阻止服务启动
        raise RuntimeError("Nacos配置加载失败，服务退出。")


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 记录请求
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 记录响应
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s"
            }
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "method": request.method,
                "url": str(request.url),
                "process_time": f"{process_time:.3f}s",
                "error": str(e)
            },
            exc_info=True
        )
        raise


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "error_type": type(exc).__name__
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# 示例路由
@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "healthy"}


@app.get("/")
def read_root():
    # 业务逻辑中使用加载的配置
    # db_conn = get_db_connection()
    return {"status": "ok", "app_config_keys": list(APP_CONFIG.keys())}


if __name__ == "__main__":
    # 示例启动（通常在 Docker 里使用 uvicorn main:app --host 0.0.0.0 启动）
    uvicorn.run(app, host="0.0.0.0", port=8000)
