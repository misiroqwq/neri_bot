from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageEvent
from nonebot.params import Arg, ArgStr, CommandArg, Depends
from nonebot.plugin import on_command
from nonebot.typing import T_State
from typing import List, Optional, Union
try:
    import ujson as json
except ModuleNotFoundError:
    import json


from .saucenao import get_saucenao_image
from neribot.configs.config import Plugin_Rule
from nonebot_plugin_session import EventSession
async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "search_image", session = session)



search_image = on_command("识图", block=True, priority=5, rule=rule)


async def get_image_info(mod: str, url: str):
    if mod == "saucenao":
        return await get_saucenao_image(url)


def parse_image(key: str):
    async def _key_parser(state: T_State, img: Message = Arg(key)):
        if not get_message_img(img):
            await search_image.reject_arg(key, "请发送要识别的图片！")
        state[key] = img

    return _key_parser


@search_image.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if msg:
        state["mod"] = msg
    else:
        state["mod"] = "saucenao"
    if get_message_img(event.json()):
        state["img"] = event.message


@search_image.got("img", prompt="图来！", parameterless=[Depends(parse_image("img"))])
async def _(
    bot: Bot,
    event: GroupMessageEvent,
    state: T_State,
    mod: str = ArgStr("mod"),
    img: Message = Arg("img"),
):
    img = get_message_img(img)[0]
    await search_image.send("开始处理图片...")
    msg = await get_image_info(mod, img)
    if isinstance(msg, str):
        await search_image.finish(msg, at_sender=True)
    await bot.send_group_forward_msg(
        group_id=event.group_id, 
        messages=custom_forward_msg(
            msg_list = msg, uin = event.user_id, name = str(event.user_id)
        )
    )


def custom_forward_msg(
    msg_list: List[Union[str, Message]],
    uin: Union[int, str],
    name: str,
) -> List[dict]:
    """
    说明:
        生成自定义合并消息
    参数:
        :param msg_list: 消息列表
        :param uin: 发送者 QQ
        :param name: 自定义名称
    """
    uin = int(uin)
    mes_list = []
    for _message in msg_list:
        data = {
            "type": "node",
            "data": {
                "name": name,
                "uin": f"{uin}",
                "content": _message,
            },
        }
        mes_list.append(data)
    return mes_list


def get_message_img(data: Union[str, Message]) -> List[str]:
    """
    说明:
        获取消息中所有的 图片 的链接
    参数:
        :param data: event.json()
    """
    img_list = []
    if isinstance(data, str):
        event = json.loads(data)
        if data and (message := event.get("message")):
            for msg in message:
                if msg["type"] == "image":
                    img_list.append(msg["data"]["url"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["url"])
    return img_list
