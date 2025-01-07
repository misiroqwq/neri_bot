from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg

from neribot.models.ban_model import BanConsole
#superuser指令打fluo开头

from neribot.configs.config import Plugin_Rule
from nonebot_plugin_session import EventSession
async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "fluoban", session = session, check_user=False)

fluoban = on_command("fluoban", priority=2, block=False, permission=SUPERUSER, rule=rule)
@fluoban.handle()
async def _(arg: Message = CommandArg()):
    """
    # 永久ban
    fluoban ban [user_id] -1 
    # ban 3600秒
    fluoban ban [user_id] 3600 
    # 解封
    fluoban unban [user_id] 
    """
    msg = arg.extract_plain_text().strip()
    allinfolist = msg.split(" ")
    cmd = allinfolist[0]
    user_id = allinfolist[1]
    if cmd == "ban":
        ban_time = allinfolist[2]
        await BanConsole.ban(user_id, int(ban_time))
        await fluoban.finish(f"已ban用户：{user_id} {ban_time} 秒")
    if cmd == "unban":
        await BanConsole.unban(user_id)
        await fluoban.finish(f"已unban用户：{user_id}")