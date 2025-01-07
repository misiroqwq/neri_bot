from nonebot.adapters.onebot.v11 import Bot
from typing import Optional
from nonebot.adapters.onebot.v11.message import MessageSegment
from itertools import islice
import httpx
from typing import Optional

from .sign_user import SignUser
from ._image_template import ImageTemplate

async def image_b64(b64: Optional[str]) -> MessageSegment:
    """
    说明:
        生成一个 MessageSegment.image 消息
    """
    file = b64 if b64.startswith("base64://") else ("base64://" + b64)
    return MessageSegment.image(file)

async def get_user_card(bot: Bot, group_id, user_id):
    # 返还用户nickname
    user_info: dict = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
    user_card = user_info["card"] or user_info["nickname"]
    return user_card

async def get_user_id_list(bot: Bot, group_id: str):
    member_info_dict_list = await bot.get_group_member_list(group_id = group_id)
    return [member_info_dict['user_id'] for member_info_dict in member_info_dict_list]



async def group_checking_rank(bot:Bot, group_id: str, num: int, all_rank: bool):
    if all_rank:
        #获取群成员信息，返回[{'group_id': ?, 'user_id': ?, 'nickname': '?', 'card': '?', ...}, ...]
        member_info_dict_list = await bot.get_group_member_list(group_id = group_id) 
        #将member_info_dict_list转化为{user_id: "user_card", ...}
        member_info_simple_dict = {}
        for member_info_dict in member_info_dict_list:
            user_id = member_info_dict["user_id"]
            user_card = member_info_dict["card"] or member_info_dict["nickname"]
            member_info_simple_dict[str(user_id)] = user_card


        #获取所有用户的签到次数 {user_id: 签到次数, ...}
        all_user_checkin_list = await SignUser.get_all_data()
        members_checking_count_dict = {}

        for user_id, check_in_count in all_user_checkin_list.items():
            # 从群昵称字典中查找对应的 user_card，找不到则用"***"
            user_card = member_info_simple_dict.get(user_id, "***")
            # 构建新的字典
            members_checking_count_dict[user_id] = [user_card, check_in_count]
            sorted_data = dict(sorted(members_checking_count_dict.items(), key=lambda item: item[1][1], reverse=True))
        return await get_all_rank_image("签到天数总排行榜", sorted_data, num)

    else:
        member_info_dict_list = await bot.get_group_member_list(group_id = group_id)
        members_checking_count_dict = await SignUser.get_members_checkin_count_dict(member_info_dict_list)
        return await get_rank_image("签到天数排行榜", members_checking_count_dict, num)

async def get_rank_image(title: str, data_dict: dict, num: int):
    """排行
    参数:
        title: 标题
        data_dict: 已排序数据字典
        num: 排行榜数量
    """
    if not data_dict:
        return "当前还没有人签到过哦..."
    
    #截取前几个数据
    data_dict = dict(islice(data_dict.items(), num))
    data_list = []
    i = 1
    for user_id, user_info_dict in data_dict.items():
        bytes = await get_user_avatar(int(user_id), 100)
        data_list.append(
            [
                str(i),
                (bytes, 30, 30),
                str(user_info_dict[0]),
                str(user_info_dict[1]),
            ]
        )
        i += 1
    tip = f"可在命令后添加数字指定人数"
    column_name = ["排名", "-", "名称", "签到次数"]
    return await ImageTemplate.table_page(title, tip, column_name, data_list)

async def get_all_rank_image(title: str, data_dict: dict, num: int):
    """排行
    参数:
        title: 标题
        data_dict: 已排序数据字典
        num: 排行榜数量
    """
    if not data_dict:
        return "当前还没有人签到过哦..."
    
    #截取前几个数据
    data_dict = dict(islice(data_dict.items(), num))
    data_list = []
    i = 1
    for user_id, user_info_dict in data_dict.items():
        data_list.append(
            [
                str(i),
                str(user_info_dict[0]),
                str(user_info_dict[1]),
            ]
        )
        i += 1
    tip = f"可在命令后添加数字指定人数"
    column_name = ["排名", "名称", "签到次数"]
    return await ImageTemplate.table_page(title, tip, column_name, data_list)

async def get_user_avatar(qq: int, px: int) -> Optional[bytes]:
    '''
    qq: 用户的qq号
    px: 像素，可选值：100，160，640
    '''
    url = f"http://q1.qlogo.cn/g?b=qq&nk={qq}&s={px}"
    async with httpx.AsyncClient() as client:
        for _ in range(3):
            try:
                return (await client.get(url)).content
            except TimeoutError:
                pass
    return None
