from datetime import datetime
from typing import Dict
from tortoise import fields
from neribot.services.db_context import Model


class Fortune_Database(Model):

    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    user_id = fields.CharField(255)
    """用户id"""
    group_id = fields.CharField(255)
    """群聊id"""
    fortune_time_last = fields.CharField(max_length=255, default="")
    """最后签到时间"""#用str是防止时区出错
    fortune_history: Dict[str, str] = fields.JSONField(default={})
    """签到历史"""

    class Meta:
        table = "fortune_database"
        table_description = "运势历史数据"
        unique_together = ("user_id", "group_id")

    @classmethod
    async def is_today_fortune(cls, user_id: str, group_id: str):
        """
        说明:
            签到
        说明:
            :param user: 用户
            :param impression: 增加的好感度
        """
        user, _ = await cls.get_or_create(user_id=user_id, group_id=group_id)
        today = str(datetime.now())[0:10]
        if user.fortune_time_last == today:
            return True
        return False
    
    @classmethod
    async def today_fortune(cls, user_id: str, group_id: str, card: str):
        """
        说明:
            今日运势数据保存
        说明:
            :param user_id: qq号
            :param group_id: 群号
            :param card: 运势名称
        """
        user, _ = await cls.get_or_create(user_id=user_id, group_id=group_id)
        today = str(datetime.now())[0:10]
        user.fortune_time_last = today #确定今天运势

        history = user.fortune_history
        history[today] = card
        user.fortune_history = history #写入历史数据

        await user.save()

    @classmethod
    async def get_user_history(cls, gid: str, uid: str):
        # 使用 `filter` 获取符合条件的用户，通常返回一个 QuerySet
        user = await cls.filter(group_id=gid, user_id=uid).first()  # 使用 `first()` 获取第一个匹配的对象
        
        if user:
            return user.fortune_history  # 访问 `fortune_history` 属性
        else:
            return None  # 如果没有找到用户，返回 None
    @classmethod
    async def get_group_history(cls, gid: str):
        query = cls.filter(group_id=gid)
        value_list = await query.all().values_list("user_id", "group_id", "fortune_history")  # type: ignore
        data_list = []
        for value in value_list:
            data_list.append([value[0],value[2]])
        return data_list


    @classmethod
    async def _run_script(cls):
        return ["ALTER TABLE sign_group_users RENAME COLUMN user_qq TO user_id;",  # 将user_id改为user_id
                "ALTER TABLE sign_group_users ALTER COLUMN user_id TYPE character varying(255);",
                # 将user_id字段类型改为character varying(255)
                "ALTER TABLE sign_group_users ALTER COLUMN group_id TYPE character varying(255);"
                ]
