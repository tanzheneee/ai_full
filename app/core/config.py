# app/core/config.py (简化版，依赖 PyYAML)
import yaml

# 全局存储 Nacos 加载的配置
GLOBAL_CONFIG = {}


def load_global_config(config_str: str):
    """解析 Nacos 拉取的配置字符串，并设置全局变量"""
    global GLOBAL_CONFIG

    # ⚠️ 实际项目中需要安装 PyYAML：pip install PyYAML
    try:
        data = yaml.safe_load(config_str)
        GLOBAL_CONFIG.update(data)
        print("Configuration successfully parsed.")
    except Exception as e:
        raise ValueError(f"Failed to parse configuration: {e}")


def get_db_url() -> str:
    """从全局配置中获取数据库连接 URL"""
    # 使用 .get() 确保键不存在时不会报错
    return GLOBAL_CONFIG.get('database', {}).get('url')