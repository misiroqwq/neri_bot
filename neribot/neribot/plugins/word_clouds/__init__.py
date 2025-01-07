
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple
from typing import List
import pytz
from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.params import Command, CommandArg
from .data_source import draw_word_cloud, get_list_msg, AtList
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from nonebot_plugin_session import EventSession
from neribot.configs.config import Plugin_Rule

async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "word_clouds", session = session)


wordcloud = on_command(
    "wordcloud",
    aliases={
        "词云",
        "今日词云",
        "昨日词云",
        "本周词云",
        "本月词云",
        "年度词云",
        "我的今日词云",
        "我的昨日词云",
        "我的本周词云",
        "我的本月词云",
        "我的年度词云",
        "添加用户词典",
        "查看用户词典",
    },
    block=True,
    priority=5,
    rule=rule
)
@wordcloud.handle()
async def handle_first_receive(
    event: GroupMessageEvent, 
    at_list: List[int] = AtList(),
    commands: Tuple[str, ...] = Command(),
    args: Message = CommandArg(),
    ):
    #基本命令情况
    command = commands[0]
    group_id = str(event.group_id)

    #确定时间范围
    dt = datetime.now().astimezone()
    state_stop = dt
    state_start = 0
    if "今日" in command :
        state_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif "昨日" in command:
        state_stop = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        state_start = state_stop - timedelta(days=1)
    elif "本周" in command:
        state_start = dt.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=dt.weekday())
    elif "本月" in command:
        state_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif "年度" in command:
        state_start = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    #用户词典相关
    elif "用户词典" in command:
        userdict_file = Path(__file__).parent / "userdict.json"
        userdict_dict = json.loads(userdict_file.read_text("utf-8"))
        if command == "添加用户词典":
            plaintext = args.extract_plain_text().strip()
            if plaintext:
                allinfolist = plaintext.split(" ")
                userdict_dict[group_id] = userdict_dict.get(group_id, []) + allinfolist
                userdict_file.write_text(json.dumps(userdict_dict, indent = 4, ensure_ascii = False),  encoding="utf-8")
                await wordcloud.finish(f"添加用户词典“{plaintext}”成功")
            else:
                await wordcloud.finish("参数不足")
                
        elif command == "查看用户词典":
            tmp_dict = userdict_dict.get(group_id,[])
            await wordcloud.finish(f"当前词典：{tmp_dict}")

    #handle
    if not state_start:
        return
    state_at_qq = at_list[0] if at_list else 0 #是否有at
    state_my = True if command.startswith("我的") else False #是否我的

    #确定操作对象
    if state_my:
        user_id = int(state_at_qq) if state_at_qq else int(event.user_id)
    else:
        user_id = None


    # 将时间转换到 东八 时区
    messages = await get_list_msg(
        user_id,
        int(event.group_id),
        days=(
            state_start.astimezone(pytz.timezone("Asia/Shanghai")),
            state_stop.astimezone(pytz.timezone("Asia/Shanghai")),
        ),
    )

    if messages:
        image_bytes = await draw_word_cloud(messages, get_driver().config, group_id)
        if image_bytes:
            await wordcloud.finish(MessageSegment.image(image_bytes), at_sender=True)
        else:
            await wordcloud.finish("生成词云失败")
    else:
        await wordcloud.finish("没有获取到词云数据")


