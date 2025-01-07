import random
from io import BytesIO
from pathlib import Path
from collections.abc import Callable

from pydantic import BaseModel
from PIL.ImageFont import FreeTypeFont

from ._build_image import BuildImage
from nonebot.log import logger

class RowStyle(BaseModel):
    font: FreeTypeFont | str | Path | None = "HYWenHei-85W.ttf"
    """字体"""
    font_size: int = 20
    """字体大小"""
    font_color: str | tuple[int, int, int] = (0, 0, 0)
    """字体颜色"""

    class Config:
        arbitrary_types_allowed = True


class ImageTemplate:
    color_list = ["#C2CEFE", "#FFA94C", "#3FE6A0", "#D1D4F5"]  # noqa: RUF012

    @classmethod
    async def table_page(
        cls,
        head_text: str,
        tip_text: str | None,
        column_name: list[str],
        data_list: list[list[str | int | tuple[Path | BuildImage, int, int]]],
        row_space: int = 35,
        column_space: int = 30,
        padding: int = 5,
        text_style: Callable[[str, str], RowStyle] | None = None,
    ) -> BuildImage:
        """表格页

        参数:
            head_text: 标题文本.
            tip_text: 标题注释.
            column_name: 表头列表.
            data_list: 数据列表.
            row_space: 行间距.
            column_space: 列间距.
            padding: 文本内间距.
            text_style: 文本样式.

        返回:
            BuildImage: 表格图片
        """
        font = BuildImage.load_font(font_size=50)

        min_width, _ = BuildImage.get_text_size(head_text, font)
        table = await cls.table(
            column_name,
            data_list,
            row_space,
            column_space,
            padding,
            text_style,
        )
        await table.circle_corner()
        table_bk = BuildImage(
            max(table.width, min_width) + 100, table.height + 50, "#EAEDF2"
        )
        await table_bk.paste(table, center_type="center")
        height = table_bk.height + 200
        background = BuildImage(table_bk.width, height, (255, 255, 255), font_size=50)
        await background.paste(table_bk, (0, 200))
        await background.text((0, 50), head_text, "#334762", center_type="width")
        if tip_text:
            text_image = await BuildImage.build_text_image(tip_text, size=22)
            await background.paste(text_image, (0, 110), center_type="width")
        return background

    @classmethod
    async def table(
        cls,
        column_name: list[str],
        data_list: list[list[str | int | tuple[Path | BuildImage, int, int]]],
        row_space: int = 25,
        column_space: int = 10,
        padding: int = 5,
        text_style: Callable[[str, str], RowStyle] | None = None,
    ) -> BuildImage:
        """表格

        参数:
            column_name: 表头列表
            data_list: 数据列表
            row_space: 行间距.
            column_space: 列间距.
            padding: 文本内间距.
            text_style: 文本样式.
            min_width: 最低宽度

        返回:
            BuildImage: 表格图片
        """
        font = BuildImage.load_font("HYWenHei-85W.ttf", 20)
        column_data = []
        for i in range(len(column_name)):
            c = []
            for item in data_list:
                if len(item) > i:
                    c.append(
                        item[i] if isinstance(item[i], tuple | list) else str(item[i])
                    )
                else:
                    c.append("")
            column_data.append(c)
        build_data_list = []
        _, base_h = BuildImage.get_text_size("A", font)
        for i, column_list in enumerate(column_data):
            name_width, _ = BuildImage.get_text_size(column_name[i], font)
            _temp = {"width": name_width, "data": column_list}
            for s in column_list:
                if isinstance(s, tuple):
                    w = s[1]
                else:
                    w, _ = BuildImage.get_text_size(str(s), font)
                if w > _temp["width"]:
                    _temp["width"] = w
            build_data_list.append(_temp)
        column_image_list = []
        column_name_image_list: list[BuildImage] = []
        for i, data in enumerate(build_data_list):
            column_name_image = await BuildImage.build_text_image(
                column_name[i], font, 12, "#C8CCCF"
            )
            column_name_image_list.append(column_name_image)
        max_h = max(c.height for c in column_name_image_list)
        for i, data in enumerate(build_data_list):
            width = data["width"] + padding * 2
            height = (base_h + row_space) * (len(data["data"]) + 1) + padding * 2
            background = BuildImage(width, height, (255, 255, 255))
            column_name_image = column_name_image_list[i]
            await background.paste(column_name_image, (0, 20), center_type="width")
            cur_h = max_h + row_space + 20
            for item in data["data"]:
                style = RowStyle(font=font)
                if text_style:
                    style = text_style(column_name[i], item)
                if isinstance(item, tuple | list):
                    """图片"""
                    data, width, height = item
                    image_ = None
                    if isinstance(data, Path):
                        image_ = BuildImage(width, height, background=data)
                    elif isinstance(data, bytes):
                        image_ = BuildImage(width, height, background=BytesIO(data))
                    elif isinstance(data, BuildImage):
                        image_ = data
                    if image_:
                        await background.paste(image_, (padding, cur_h))
                else:
                    await background.text(
                        (padding, cur_h),
                        item if item is not None else "",
                        style.font_color,
                        font=style.font,
                        font_size=style.font_size,
                    )
                cur_h += base_h + row_space
            column_image_list.append(background)
        return await BuildImage.auto_paste(
            column_image_list, len(column_image_list), column_space
        )

    @classmethod
    async def __build_text_image(
        cls,
        text: str,
        width: int,
        height: int,
        font: FreeTypeFont,
        font_color: str | tuple[int, int, int] = (0, 0, 0),
        color: str | tuple[int, int, int] = (255, 255, 255),
    ) -> BuildImage:
        """文本转图片

        参数:
            text: 文本
            width: 宽度
            height: 长度
            font: 字体
            font_color: 文本颜色
            color: 背景颜色

        返回:
            BuildImage: 文本转图片
        """
        _, h = BuildImage.get_text_size("A", font)
        A = BuildImage(width, height, color=color)
        cur_h = 0
        for s in text.split("\n"):
            text_image = await BuildImage.build_text_image(
                s, font, font_color=font_color
            )
            await A.paste(text_image, (0, cur_h))
            cur_h += h
        return A

    @classmethod
    async def __get_text_size(
        cls,
        text: str,
        font: FreeTypeFont,
    ) -> tuple[int, int]:
        """获取文本所占大小

        参数:
            text: 文本
            font: 字体

        返回:
            tuple[int, int]: 宽, 高
        """
        width = 0
        height = 0
        _, h = BuildImage.get_text_size("A", font)
        for s in text.split("\n"):
            s = s.strip() or "A"
            w, _ = BuildImage.get_text_size(s, font)
            width = max(width, w)
            height += h
        return width, height