from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State
from neribot.configs.config import Plugin_Rule
from nonebot_plugin_session import EventSession
async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "withdraw", session = session)


withdraw_msg = on_command("撤回", priority=3, block=True)


@withdraw_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if event.reply:
        await bot.delete_msg(message_id=event.reply.message_id)
