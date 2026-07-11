"""
Redis 缓存服务
AI生成：Redis 连接管理与缓存操作封装
人工修改：增加 JSON 序列化支持、缓存降级逻辑
"""
import json
import redis.asyncio as redis
from app.config import settings


class RedisCache:
    """Redis 缓存工具类，用于 API 响应缓存和任务队列"""

    _instance = None
    _client = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """获取 Redis 单例连接"""
        if cls._client is None:
            cls._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None

    @classmethod
    async def get(cls, key: str):
        """获取缓存值（自动 JSON 反序列化）"""
        try:
            client = cls.get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.ConnectionError, json.JSONDecodeError):
            return None

    @classmethod
    async def set(cls, key: str, value, ttl: int = 300):
        """设置缓存值（自动 JSON 序列化，默认 5 分钟过期）"""
        try:
            client = cls.get_client()
            await client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
            return True
        except redis.ConnectionError:
            return False

    @classmethod
    async def delete(cls, key: str):
        """删除缓存"""
        try:
            client = cls.get_client()
            await client.delete(key)
            return True
        except redis.ConnectionError:
            return False

    @classmethod
    async def health_check(cls) -> bool:
        """检测 Redis 连接是否正常"""
        try:
            client = cls.get_client()
            return await client.ping()
        except redis.ConnectionError:
            return False
