
from nonebot_plugin_session import EventSession
from neribot.models.ban_model import BanConsole
from neribot.models.plugins_control_model import PluginsGroupControl
from nonebot.log import logger

# 注意事项
# priority在5-10之间会被检测恶意触发
# priority = 2 时为超级用户指令
# priority = 1 时为被动指令


NICKNAME = "音理"

ADMIN_GROUP = 123

class Plugin_Rule: 
    @classmethod
    async def get_rule(cls, plugin_name: str, session: EventSession, check_user = True):
        if not session.id2: # 非群聊直接返回false
            return False
        
        # 插件是否打开, 同时检测总开关
        if not await PluginsGroupControl.is_plugin_enable(str(session.id2), plugin_name):
             return False
        # 用户黑名单控制
        if check_user:
            if await BanConsole.is_ban(str(session.id1)): 
                return False

        return True