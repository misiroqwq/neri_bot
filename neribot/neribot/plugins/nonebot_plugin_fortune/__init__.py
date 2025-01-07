from pathlib import Path
from typing import Dict
from nonebot.params import CommandArg
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    Message,
    MessageSegment,
)
from nonebot.permission import SUPERUSER
from .data_source import FortuneManager, fortune_manager
from .models import Fortune_Database
from .utils import luck_history_map
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from pathlib import Path
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

custom_fortune_file = Path(__file__).parent / "customfortune.json"
custom_fortune_dict = json.loads(custom_fortune_file.read_text("utf-8")) if custom_fortune_file.is_file() else {}
from nonebot_plugin_apscheduler import scheduler

from neribot.configs.config import Plugin_Rule
from nonebot_plugin_session import EventSession


async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "fortune", session = session)
async def rule2(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "fortune_admin", session = session, check_user=False)



general_divine = on_command("今日运势", aliases={"抽签", "运势"}, block = True, permission=GROUP, priority=5, rule=rule)
@general_divine.handle()
async def _(event: GroupMessageEvent):
    gid: str = str(event.group_id)
    uid: str = str(event.user_id)
    if await Fortune_Database.is_today_fortune(user_id=uid, group_id=gid):#处理是否多次运势
        image_file, card= await fortune_manager.divine(gid=gid, uid=uid, is_today_fortuned=True, 
                                                       custom_title=None, custom_text=None)
        if image_file:
            msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
        else:
            await general_divine.finish("今日运势生成出错……")
    else:
        #获取图片和card
        custom_title, custom_text = await Custom_fortune_get(gid=gid, uid=uid)
        image_file, card= await fortune_manager.divine(gid=gid, uid=uid, is_today_fortuned=False,
                                                    custom_title=custom_title, custom_text=custom_text)
        if image_file:
            msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
            await Fortune_Database.today_fortune(user_id = uid, group_id = gid, card = card)
        else:
            await general_divine.finish("今日运势生成出错……")
    await general_divine.finish(msg, at_sender=True)

history_fortune = on_command("历史运势", aliases={"历史抽签"}, block = True, permission=GROUP, priority=5, rule=rule)
@history_fortune.handle()
async def _(event: GroupMessageEvent):
    data = await Fortune_Database.get_user_history(event.group_id, event.user_id)
    #data to list
    numbers = await history_data_to_numbers(data)
    if numbers:
        image = await luck_history_map(numbers)
        await history_fortune.finish(MessageSegment.image(image))

Custom_fortune = on_command("定制运势", aliases={"定制抽签"}, permission=SUPERUSER, priority=3, rule=rule2)
@Custom_fortune.handle() #"定制运势 gid uid title text"
async def _(arg: Message = CommandArg()):
    command = arg.extract_plain_text().strip()
    allinfolist = command.split(" ")
    gid = allinfolist[0]
    uid = allinfolist[1]
    title = allinfolist[2]
    text = allinfolist[3]

    custom_fortune_dict[f"{gid}_{uid}"] = [title, text]

    custom_fortune_file.write_text(json.dumps(custom_fortune_dict, indent = 4, ensure_ascii = False),  encoding="utf-8")
    await Custom_fortune.finish(f"定制运势已添加：\n群：{gid}\n用户：{uid}\n标题：{title}\n内容：{text}")

async def Custom_fortune_get(gid: str, uid: str):
    content = custom_fortune_dict.get(f"{gid}_{uid}", [])
    if content:
        title = content[0]
        text = content[1]
        if title == "None":
            title = None
        if text == "None":
            text = None
        return title, text
    else:
        return None, None

async def history_data_to_numbers(data: Dict):
    if not data:
        return False
    lucktonum = {
    "関係運": 0,
    "全体運": 0,
    "勉強運": 0,
    "金運": 0,
    "仕事運": 0,
    "恋愛運": 0,
    "総合運": 0,
    "大吉": 10,
    "中吉": 9,
    "小吉": 8,
    "吉": 7,
    "半吉": 6,
    "末吉": 5,
    "末小吉": 4,
    "凶": -6,
    "小凶": -7,
    "半凶": -8,
    "末凶": -9,
    "大凶": -10
    }
    numbers = []
    for value in data.values():
        num = lucktonum.get(value, -66)
        numbers.append(num)
    return numbers

#fortune_rank_good = on_command("运势排行吉", permission=GROUP, priority=5)
#@fortune_rank_good.handle()
#async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
#    msg = arg.extract_plain_text().strip()
#    pattern = re.compile(r'[0-9]+')
#    try:
#        num = int(pattern.search(msg)[0])
#    except TypeError:
#        num = 20
#        
#    if num < 10:
#        num = 10
#    elif num > 50:
#        num = 50
#
#    raw_data = await Fortune_Database.get_group_history(event.group_id)
#    #计算每个用户的平均值
#    ##获取numbers
#    user_avgnum_list = []
#    for user in raw_data:
#        user_id = user[0]
#        data = user[1]
#        numbers =await history_data_to_numbers(data)
#        total_score = 0
#        if numbers:
#            for num_ in numbers:
#                if num_>-15:
#                    total_score += num_
#            score_avg=round(total_score/len(numbers),2)+10
#            user_avgnum_list.append([user_id,score_avg])
#    _image = await init_rank("运势排行吉", user_avgnum_list, event.group_id, num, False)
#    if _image:
#        await fortune_rank_good.finish(image(b64=_image.pic2bs4()))


#fortune_rank_bad = on_command("运势排行凶", permission=GROUP, priority=5)
#@fortune_rank_bad.handle()
#async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
#    msg = arg.extract_plain_text().strip()
#    pattern = re.compile(r'[0-9]+')
#    try:
#        num = int(pattern.search(msg)[0])
#    except TypeError:
#        num = 20
#        
#    if num < 10:
#        num = 10
#    elif num > 50:
#        num = 50
#
#    raw_data = await Fortune_Database.get_group_history(event.group_id)
#    #计算每个用户的平均值
#    ##获取numbers
#    user_avgnum_list = []
#    for user in raw_data:
#        user_id = user[0]
#        data = user[1]
#        numbers =await history_data_to_numbers(data)
#        total_score = 0
#        if numbers:
#            for num_ in numbers:
#                if num_>-15:
#                    total_score += num_
#            score_avg=-round(total_score/len(numbers),2)+10
#            user_avgnum_list.append([user_id,score_avg])
#    _image = await init_rank("运势排行凶", user_avgnum_list, event.group_id, num, False)
#    if _image:
#        await fortune_rank_good.finish(MessageSegment.image(_image.pic2bs4()))



# 清空昨日生成的图片
@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
    await FortuneManager.clean_out_pics()
