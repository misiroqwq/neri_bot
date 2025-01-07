from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, Message
from nonebot.params import CommandArg

from neribot.configs.config import NICKNAME
import random
import asyncio
from neribot.configs.config import Plugin_Rule
from nonebot_plugin_session import EventSession
async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "roll", session = session)


roll = on_command("roll", priority=5, block=True, rule=rule)


@roll.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if not msg:
        await roll.finish(f"roll: {random.randint(0, 100)}", at_sender=True)
    user_name = event.sender.card or event.sender.nickname
    await roll.send(
        random.choice(
            [
                "转动命运的齿轮，拨开眼前迷雾...",
                f"启动吧，命运的水晶球，为{user_name}指引方向！",
                "嗯哼，在此刻转动吧！命运！",
                f"在此祈愿，请为{user_name}降下指引...",
            ]
        )
    )
    await asyncio.sleep(1)
    x = random.choice(msg)
    await roll.send(
        random.choice(
            [
                f"让{NICKNAME}看看是什么结果！答案是：‘{x}’",
                f"根据命运的指引，接下来{user_name} ‘{x}’ 会比较好",
                f"祈愿被回应了！是 ‘{x}’！",
                f"结束了，{user_name}，命运之轮停在了 ‘{x}’！",
            ]
        )
    )
