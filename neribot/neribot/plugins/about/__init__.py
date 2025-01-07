
from nonebot import on_command
from neribot.configs.config import NICKNAME
from neribot.configs.config import Plugin_Rule
from nonebot.rule import to_me
from nonebot_plugin_session import EventSession
async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "about", session = session)


self_introduction = on_command(
    "about", 
    aliases={"关于"}, 
    rule=to_me(), 
    priority=5, 
    block=True
)


@self_introduction.handle()
async def _(session: EventSession):
    if not await rule(session = session):
        return
    await self_introduction.finish("https://github.com/misiroqwq/neri_bot")




