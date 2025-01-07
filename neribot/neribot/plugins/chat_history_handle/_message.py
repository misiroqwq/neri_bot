from io import BytesIO
from pathlib import Path

import nonebot
from pydantic import BaseModel
from nonebot_plugin_alconna import (
    At,
    Text,
    AtAll,
    Image,
    Video,
    Voice,
    UniMessage,
)

from ._build_image import BuildImage

driver = nonebot.get_driver()

MESSAGE_TYPE = (
    str
    | int
    | float
    | Path
    | bytes
    | BytesIO
    | BuildImage
    | At
    | AtAll
    | Image
    | Text
    | Voice
    | Video
)


class Config(BaseModel):
    image_to_bytes: bool = False


class MessageUtils:
    @classmethod
    def __build_message(cls, msg_list: list[MESSAGE_TYPE]) -> list[Text | Image]:
        """构造消息

        参数:
            msg_list: 消息列表

        返回:
            list[Text | Text]: 构造完成的消息列表
        """
        config = nonebot.get_plugin_config(Config)
        message_list = []
        for msg in msg_list:
            if isinstance(msg, Image | Text | At | AtAll | Video | Voice):
                message_list.append(msg)
            elif isinstance(msg, str | int | float):
                message_list.append(Text(str(msg)))
            elif isinstance(msg, Path):
                if msg.exists():
                    if config.image_to_bytes:
                        image = BuildImage.open(msg)
                        message_list.append(Image(raw=image.pic2bytes()))
                    else:
                        message_list.append(Image(path=msg))
            elif isinstance(msg, bytes):
                message_list.append(Image(raw=msg))
            elif isinstance(msg, BytesIO):
                message_list.append(Image(raw=msg))
            elif isinstance(msg, BuildImage):
                message_list.append(Image(raw=msg.pic2bytes()))
        return message_list

    @classmethod
    def build_message(
        cls, msg_list: MESSAGE_TYPE | list[MESSAGE_TYPE | list[MESSAGE_TYPE]]
    ) -> UniMessage:
        """构造消息

        参数:
            msg_list: 消息列表

        返回:
            UniMessage: 构造完成的消息列表
        """
        message_list = []
        if not isinstance(msg_list, list):
            msg_list = [msg_list]
        for m in msg_list:
            _data = m if isinstance(m, list) else [m]
            message_list += cls.__build_message(_data)  # type: ignore
        return UniMessage(message_list)

