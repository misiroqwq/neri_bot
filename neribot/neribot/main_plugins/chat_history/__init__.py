from nonebot import on_message
from nonebot_plugin_alconna import UniMsg
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_session import EventSession
from neribot.models.chat_history_model import ChatHistory
from nonebot.log import logger
from neribot.configs.config import Plugin_Rule

async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "chat_history", session = session, check_user=False)

TEMP_LIST = []
chat_history_model = on_message(priority=1, block=False, rule=rule)
@chat_history_model.handle()
async def _(message: UniMsg, session: EventSession):
    group_id = session.id2
    TEMP_LIST.append(
        ChatHistory(
            user_id=session.id1,
            group_id=group_id,
            text=str(message),
        )
    )


@scheduler.scheduled_job(
    "interval",
    minutes=1,
)
async def _():
    try:
        message_list = TEMP_LIST.copy()
        TEMP_LIST.clear()
        if message_list:
            await ChatHistory.bulk_create(message_list)
    except Exception as e:
        logger.error(f"定时批量添加聊天记录出错{e}")
