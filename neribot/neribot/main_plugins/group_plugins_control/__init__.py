from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg


from neribot.models.plugins_control_model import PluginsGroupControl

from neribot.configs.config import ADMIN_GROUP
from nonebot_plugin_session import EventSession
async def rule(session: EventSession) -> bool:
    if session.id2 == ADMIN_GROUP:
        return True
    return False

#superuser指令打fluo开头
fluoplugins = on_command("fluoplugins", priority=2, block=False, permission=SUPERUSER, rule=rule)
@fluoplugins.handle()
async def _(arg: Message = CommandArg()):
    """
    总开关 开: 
        fluoplugins main [group_id] 1 
    总开关 开: 
        fluoplugins main [group_id] 0 
    总开关获取:
        fluoplugins mainget [group_id]
    更新插件控制列表:
        fluoplugins plugins [group_id] plugin_1 plugin_2 plugin_3 ...
    获取已激活插件:
        fluoplugins pluginsget [group_id]
    """
    msg = arg.extract_plain_text().strip()
    allinfolist = msg.split(" ")
    cmd = allinfolist[0]
    if cmd == "main":
        group_id = allinfolist[1]
        switch = int(allinfolist[2])
        await PluginsGroupControl.update_main_switch(group_id, switch)
        await fluoplugins.finish(f"总开关：{switch}")
    if cmd == "maingey":
        group_id = allinfolist[1]
        switch = await PluginsGroupControl.is_main_switch_on(group_id)
        await fluoplugins.finish(f"总开关状态：{switch}")
    if cmd == "plugins":
        group_id = allinfolist[1]
        enable_plugins = allinfolist[2:]
        await PluginsGroupControl.update_enable_plugins(group_id, enable_plugins)
        await fluoplugins.finish(f"已更新")
    if cmd == "pluginsget":
        group_id = allinfolist[1]
        enable_plugins_list = await PluginsGroupControl.get_enable_plugins(group_id)
        if enable_plugins_list:
            text = ' '.join(enable_plugins_list)
            await fluoplugins.finish(text)
        else:
            await fluoplugins.finish("无")