from typing_extensions import Self
from tortoise import fields
from neribot.services.db_context import Model
import time
from nonebot.log import logger


class BanConsole(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    user_id = fields.CharField(255, null=True)
    """用户id"""
    ban_time = fields.BigIntField()
    """ban开始的时间"""
    duration = fields.BigIntField()
    """ban时长"""
    class Meta:  # type: ignore
        table = "ban_console"
        table_description = "封禁人员/群组数据表"


    @classmethod
    async def _get_data(cls, user_id: str) -> Self | None:
        """获取数据
        参数:
            user_id: 用户id
        """
        if user_id:
            return await cls.get_or_none(user_id=user_id)
        
    @classmethod
    async def check_ban_time(cls, user_id: str) -> int:
        """检测用户被ban时长
        参数:
            user_id: 用户id
        返回:
            int: ban剩余时长，-1时为永久ban，0表示未被ban
        """
        user = await cls._get_data(user_id)
        if user:
            if user.duration == -1:
                return -1
            _time = time.time() - (user.ban_time + user.duration)
            return 0 if _time > 0 else int(time.time() - user.ban_time - user.duration)
        return 0

    @classmethod
    async def is_ban(cls, user_id: str) -> bool:
        """判断用户是否被ban

        参数:
            user_id: 用户id

        返回:
            bool: 是否被ban
        """
        if await cls.check_ban_time(user_id):
            return True
        else:
            await cls.unban(user_id)
        return False

    @classmethod
    async def ban(cls, user_id: str, duration: int,):
        """ban掉目标用户

        参数:
            user_id: 用户id
            duration: 时长，-1时为永久
        """
        target = await cls._get_data(user_id)
        if target:
            await cls.unban(user_id)
        await cls.create(
            user_id=user_id,
            ban_time=int(time.time()),
            duration=duration,
        )

    @classmethod
    async def unban(cls, user_id: str) -> bool:
        """unban用户
        参数:
            user_id: 用户id
        返回:
            bool: 是否被ban
        """
        user = await cls._get_data(user_id)
        if user:
            await user.delete()
            return True
        return False
