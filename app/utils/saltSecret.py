import hashlib
import secrets

# 哈希加密示例
def hash_password(password):
    # 生成随机盐值
    salt = secrets.token_hex(16)
    # 加盐哈希
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + hashed.hex()

# 验证密码
def verify_password(stored_password, provided_password):
    salt = stored_password[:32]  # 提取盐值
    stored_hash = stored_password[32:]  # 提取哈希值
    hash_attempt = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return hash_attempt.hex() == stored_hash