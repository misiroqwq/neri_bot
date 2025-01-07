from datetime import datetime, timedelta
import pytz
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    Arparma,
    Match,
    Option,
    Query,
    on_alconna,
    store_true,
)
from nonebot.log import logger
from nonebot_plugin_session import EventSession
from neribot.models.chat_history_model import ChatHistory
from neribot.configs.config import Plugin_Rule
from nonebot.adapters.onebot.v11 import Bot
from ._image_template import ImageTemplate
from ._message import MessageUtils
async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "chat_history_handle", session = session)

msg_handler = on_alconna(
    Alconna(
        "消息排行",
        Option("--des", action=store_true, help_text="逆序"),
        Args["type?", ["日", "周", "月", "年"]]["count?", int, 10],
    ),
    aliases={"消息统计"},
    priority=5,
    block=True,
    rule=rule
)
msg_handler.shortcut(
    r"(?P<type>['日', '周', '月', '年'])?消息(排行|统计)\s?(?P<cnt>\d+)?",
    command="消息排行",
    arguments=["{type}", "{cnt}"],
    prefix=True,
)
@msg_handler.handle()
async def _(
    bot: Bot,
    session: EventSession,
    arparma: Arparma,
    type: Match[str],
    count: Query[int] = Query("count", 10),
):
    group_id = session.id3 or session.id2
    time_now = datetime.now()
    date_scope = None
    zero_today = time_now - timedelta(
        hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second
    )
    date = type.result if type.available else None
    if date:
        if date in ["日"]:
            date_scope = (zero_today, time_now)
        elif date in ["周"]:
            date_scope = (time_now - timedelta(days=7), time_now)
        elif date in ["月"]:
            date_scope = (time_now - timedelta(days=30), time_now)
    column_name = ["名次", "昵称", "发言次数"]
    if rank_data := await ChatHistory.get_group_msg_rank(
        group_id, count.result, "DES" if arparma.find("des") else "DESC", date_scope
    ):
        idx = 1
        data_list = []
        for uid, num in rank_data:
            user_name = await get_user_name(bot = bot, group_id = group_id, user_id = uid)
            if not user_name:
                continue
            data_list.append([idx, user_name, num])
            idx += 1
        if not date_scope:
            if date_scope := await ChatHistory.get_group_first_msg_datetime(group_id):
                date_scope = date_scope.astimezone(
                    pytz.timezone("Asia/Shanghai")
                ).replace(microsecond=0)
            else:
                date_scope = time_now.replace(microsecond=0)
            date_str = f"{str(date_scope).split('+')[0]} - 至今"
        else:
            date_str = f"{date_scope[0].replace(microsecond=0).strftime('%Y-%m-%d %H:%M')} - {date_scope[1].replace(microsecond=0).strftime('%Y-%m-%d %H:%M')}"
        
        A = await ImageTemplate.table_page(
            f"消息排行({count.result})", date_str, column_name, data_list
        )
        await MessageUtils.build_message(A).finish(reply_to=False)
    await MessageUtils.build_message("群组消息记录为空...").finish()

async def get_user_name(bot: Bot, group_id: int, user_id: int):
    # 返还用户nickname
    try:
        user_info: dict = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        user_card = user_info["card"]
        if not user_card:
            user_card = user_info["nickname"]
        return user_card
    except Exception:
        return ''
