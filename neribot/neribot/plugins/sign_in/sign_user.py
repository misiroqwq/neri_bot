from datetime import datetime
from typing import Union
from tortoise import fields
from neribot.services.db_context import Model

class SignUser(Model):

    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    user_id = fields.CharField(255)
    """用户id"""
    checkin_count = fields.IntField(default=0)
    """签到次数"""
    checkin_time_last = fields.CharField(255)
    """最后签到时间"""

    class Meta:
        table = "sign_users"
        table_description = "用户签到数据表"

    @classmethod
    async def custom_get_or_create(cls, user_id: str):
        user = await cls.filter(user_id=user_id).first()
        if user is None:
            user = await cls.create(user_id=user_id, checkin_count=0, checkin_time_last='1')
        return user

    @classmethod
    async def custom_get_or_none(cls, user_id: str):
        user = await cls.filter(user_id=user_id).first()
        return user if user else False

    @classmethod
    async def get_user(cls, user_id: str):
        """
        说明:
            签到
        说明:
            :param user_id: 用户qq号
        """
        user = await cls.custom_get_or_none(user_id=user_id)
        if user:
            return user
        return False

    @classmethod
    async def sign(cls, user_id: str):
        """
        说明:
            签到
        说明:
            :param user_id: 用户qq号
        """
        user = await cls.custom_get_or_create(user_id=user_id)  # 解包元组
        user.checkin_count = user.checkin_count + 1
        sign_date = str(datetime.now().strftime("%Y%m%d"))
        user.checkin_time_last = sign_date
        await user.save(update_fields=["checkin_time_last","checkin_count"])

    @classmethod
    async def get_members_checkin_count_dict(cls, member_info_dict_list: dict) -> dict:
        """
        说明:
            获取该群所有用户 id 及对应 签到次数
        参数:
            :param member_list: 群员qq列表
        返回:
            {user_id: [昵称, 签到次数], ...}
        """
        members_checking_count_dict = {}   
        for member_info_dict in member_info_dict_list:
            user_id = str(member_info_dict['user_id'])
            user = await cls.custom_get_or_none(user_id=user_id)
            if user:
                user_card = member_info_dict["card"] or member_info_dict["nickname"]
                members_checking_count_dict[user_id] = [user_card, user.checkin_count]
        #按 checkin_count 从大到小排序
        sorted_data = dict(sorted(members_checking_count_dict.items(), key=lambda item: item[1][1], reverse=True))
        return sorted_data
    
    @classmethod
    async def get_all_data(cls):
        """
        说明:
            获取所有用户的及签到次数
        返回：
            {user_id: 签到次数, ...}
        """

        value_list = await cls.all().values_list("user_id", "checkin_count")  # type: ignore
        data_dict = {}
        for value in value_list:
            data_dict[value[0]] = int(value[1])
        return data_dict
        
    @classmethod
    async def get_checkin_count_rank(cls, rank_user: str, member_list: Union[int, str]) -> int:
        """
        说明:
            获取该用户在该列表用户下的排行
        """
        rank_user_data = await cls.custom_get_or_none(user_id=str(rank_user))
        rank_user_checking_count = rank_user_data.checkin_count
        members_checking_count_list = []
        if member_list:
            for member_id in member_list:
                member = await cls.custom_get_or_none(user_id=str(member_id))
                if member:
                    members_checking_count_list.append(member.checkin_count)
            if members_checking_count_list:
                members_checking_count_list.sort(reverse=True)
                index = members_checking_count_list.index(rank_user_checking_count)
                return index + 1
            else:
                return False
        else:
            return False

#下面是额外执行过的SQL语句

#CREATE SEQUENCE sign_users_id_seq
#  START WITH 1
#  INCREMENT BY 1
#  NO MINVALUE
#  NO MAXVALUE
#  CACHE 1;


#ALTER TABLE sign_users
#  ALTER COLUMN id SET DEFAULT nextval('sign_users_id_seq');
