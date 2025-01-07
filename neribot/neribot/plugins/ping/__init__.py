
from datetime import datetime
from nonebot import on_command
from neribot.configs.config import Plugin_Rule
from nonebot_plugin_session import EventSession

async def ping_rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "ping", session = session)


ping = on_command("ping", rule=ping_rule, priority=5, block=True)

@ping.handle()
async def _():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ping.finish(now)
