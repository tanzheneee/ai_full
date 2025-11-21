import bcrypt

def hash_password(password: str) -> str:
    """使用 Bcrypt 对密码进行安全哈希"""
    # 1. 对密码进行编码
    password_bytes = password.encode('utf-8')

    # 2. 生成 Salt 并进行哈希计算（bcrypt 自带 Salt）
    # gensalt() 会生成一个随机的 salt
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # 3. 将结果（Salt + Hash）解码成字符串存储
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证输入的明文密码是否与存储的哈希密码匹配"""

    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    # bcrypt.checkpw() 会自动从 hashed_password 中提取 salt 并进行比较
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)