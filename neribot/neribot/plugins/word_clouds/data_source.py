import asyncio
import os
import random
import re
from io import BytesIO
from typing import List
import jieba
import jieba.analyse
import matplotlib.pyplot as plt
import numpy as np
from emoji import replace_emoji  # type: ignore
from PIL import Image as IMG
from wordcloud import ImageColorGenerator, WordCloud
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from typing import Callable, List, Optional, Union
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import Depends
from nonebot.adapters.onebot.v11 import Message

from neribot.models.chat_history_model import ChatHistory
FONT_PATH = Path(__file__).parent / "resourece" / "STKAITI.TTF"
IMAGE_PATH = Path(__file__).parent / "resourece" / "default.png"



async def _match(
    matcher: Matcher,
    event: MessageEvent,
    msg: Optional[str],
    func: Callable,
    contain_reply: bool,
):
    _list = func(event.message)
    if event.reply and contain_reply:
        _list = func(event.reply.message)
    if not _list and msg:
        await matcher.finish(msg)
    return _list

def get_message_at(data: Union[str, Message]) -> List[int]:
    """
    说明:
        获取消息中所有的 at 对象的 qq
    参数:
        :param data: event.json(), event.message
    """
    qq_list = []
    if isinstance(data, str):
        event = json.loads(data)
        if data and (message := event.get("message")):
            for msg in message:
                if msg and msg.get("type") == "at":
                    qq_list.append(int(msg["data"]["qq"]))
    else:
        for seg in data:
            if seg.type == "at":
                qq_list.append(seg.data["qq"])
    return qq_list



def AtList(msg: Optional[str] = None, contain_reply: bool = True) -> List[int]:
    """
    说明:
        获取at列表（包括回复时），含有msg时不能为空，为空时提示并结束事件
    参数:
        :param msg: 提示文本
        :param contain_reply: 包含回复内容
    """

    async def dependency(matcher: Matcher, event: MessageEvent):
        return [
            int(x)
            for x in await _match(matcher, event, msg, get_message_at, contain_reply)
        ]

    return Depends(dependency)



async def pre_precess(msg: List[str], config) -> str:
    return await asyncio.get_event_loop().run_in_executor(
        None, _pre_precess, msg, config
    )


def _pre_precess(msg: List[str], config) -> List[str]:
    msg = " ".join([m for m in msg])

    msg = re.sub(r"\[CQ:.*?]", "", msg, flags= re.DOTALL)

    url_regex = re.compile(
        r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]"
        r"+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
    )
    msg = url_regex.sub("", msg)

    msg = re.sub(r"[\u200b]", "", msg)
    msg = re.sub("[&#9(1|3);]", "", msg)

    msg = replace_emoji(msg)
#wait
    return msg

async def draw_word_cloud(messages, config, grp):
    wordcloud_ttf = FONT_PATH

    topK = min(int(len(messages)), 100000)

    
    userdict_file = Path(__file__).parent / "userdict.json"
    userdict_dict = json.loads(userdict_file.read_text("utf-8"))
    userdict_list = userdict_dict.get(grp, [])

    for word in userdict_list:
        jieba.add_word(word)
    read_name = jieba.analyse.extract_tags(
        await pre_precess(messages, config), topK=topK, withWeight=True, allowPOS=()
    )
    name = []
    value = []
    for t in read_name:
        name.append(t[0])
        value.append(t[1])
    for i in range(len(name)):
        name[i] = str(name[i])
    dic = dict(zip(name, value))
    mask = np.array(IMG.open(IMAGE_PATH))
    wc = WordCloud(
        font_path=f"{wordcloud_ttf}",
        background_color="white",
        max_font_size=100,
        width=1920,
        height=1080,
        mask=mask,
    )
    wc.generate_from_frequencies(dic)
    image_colors = ImageColorGenerator(mask, default_color=(255, 255, 255))
    wc.recolor(color_func=image_colors)
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")

    bytes_io = BytesIO()
    img = wc.to_image()
    img.save(bytes_io, format="PNG")
    return bytes_io.getvalue()


async def get_list_msg(user_id, group_id, days):
    messages_list = await ChatHistory().get_message(
        uid=user_id, gid=group_id, type_="group", days=days
    )
    if messages_list:
        messages = [i.text for i in messages_list]
        return messages
    else:
        return False
