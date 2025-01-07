from .music_163 import get_song_id
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot import on_command

from neribot.configs.config import Plugin_Rule
from nonebot_plugin_session import EventSession
async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "music", session = session)


music_handler = on_command("点歌", priority=5, block=True, rule=rule)


@music_handler.handle()
async def handle_first_receive(state: T_State, arg: Message = CommandArg()):
    if args := arg.extract_plain_text().strip():
        state["song_name"] = args


@music_handler.got("song_name", prompt="歌名是？")
async def _(bot: Bot, event: MessageEvent, state: T_State):
    song = state["song_name"]
    song_id = await get_song_id(song)
    if not song_id:
        await music_handler.finish("没有找到这首歌！", at_sender=True)
    await music_handler.send(MessageSegment.music("163", song_id))




