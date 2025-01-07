try:
    import ujson as json
except ModuleNotFoundError:
    import json
import random
from pathlib import Path
from typing import List, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from nonebot.log import logger
copywriting_file = Path(__file__).parent / "copywriting2.json"
copywriting_dict = json.loads(copywriting_file.read_text("utf-8"))

def get_copywriting(custom_title: Union[str, None], custom_text: Union[str, None]) -> Tuple[str, str]:
    """
    Read the copywriting.json, choice a luck with a random content
    """
    if custom_title:
        title = custom_title
    else:
        title = random.choice(list(copywriting_dict.keys()))
    
    if custom_text:
        text = custom_text
    else:
        if copywriting_dict.get(title, ''):
            text: str = random.choice(copywriting_dict[title]["content"])
        else:
            text: str = "自定义文本"
    return title, text


def random_basemap() -> Path:#选一张图片
    _p: Path = Path(__file__).parent / "resource" / "img" / "hoshizora"
    images_dir: List[Path] = [i for i in _p.iterdir() if i.is_file()]
    p: Path = random.choice(images_dir)
    return p


def drawing(gid: str, uid: str, custom_title: Union[str, None], custom_text: Union[str, None]) -> Path:
    # 1. Random choice a base image
    imgPath: Path = random_basemap()
    img: Image.Image = Image.open(imgPath).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 2. Random choice a luck text with title
    title, text = get_copywriting(custom_title, custom_text)
    # 3. Draw
    font_size = 45
    color = "#F5F5F5"
    image_font_center = [140, 99]
    fontPath = {
        "title": Path(__file__).parent / "resource"/ "font" / "Mamelon.otf",
        "text": Path(__file__).parent / "resource"/ "font" / "sakura.ttf",
    }
    ttfront = ImageFont.truetype(str(fontPath["title"]), font_size)

    bbox = ttfront.getbbox(title)
    font_length = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    draw.text(
        (
            image_font_center[0] - font_length[0] / 2,
            image_font_center[1] - font_length[1] / 2,
        ),
        title,
        fill=color,
        font=ttfront,
    )

    # Text rendering
    font_size = 25
    color = "#323232"
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(str(fontPath["text"]), font_size)
    slices, result = decrement(text)

    for i in range(slices):
        font_height: int = len(result[i]) * (font_size + 4)
        textVertical: str = "\n".join(result[i])
        x: int = int(
            image_font_center[0]
            + (slices - 2) * font_size / 2
            + (slices - 1) * 4
            - i * (font_size + 4)
        )
        y: int = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)

    # Save
    outDir: Path = Path(__file__).parent / "resource" / "out"
    if not outDir.exists():
        outDir.mkdir(exist_ok=True, parents=True)

    outPath = outDir / f"{gid}_{uid}.png"

    img.save(outPath)
    return outPath, title # title == card


def decrement(text: str) -> Tuple[int, List[str]]:
    """
    Split the text, return the number of columns and text list
    TODO: Now, it ONLY fit with 2 columns of text
    """
    length: int = len(text)
    result: List[str] = []
    cardinality = 9
    if length > 4 * cardinality:
        raise Exception

    col_num: int = 1
    while length > cardinality:
        col_num += 1
        length -= cardinality

    # Optimize for two columns
    space = " "
    length = len(text)  # Value of length is changed!

    if col_num == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return col_num, [
                text[: int(length / 2)] + fillIn,
                fillIn + text[int(length / 2) :],
            ]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return col_num, [
                text[: int((length + 1) / 2)] + fillIn,
                fillIn + space + text[int((length + 1) / 2) :],
            ]

    for i in range(col_num):
        if i == col_num - 1 or col_num == 1:
            result.append(text[i * cardinality :])
        else:
            result.append(text[i * cardinality : (i + 1) * cardinality])

    return col_num, result


async def luck_history_map(numbers: List):
    #计算文字
    if len(numbers)>100:
        numbers = numbers[:100] 
    c_normal = 0
    c_bad = 0
    c_good = 0
    c_other = 0
    total_score = 0
    # 遍历数组并统计
    for num in numbers:
        if num == 0:
            c_normal += 1
        elif num < 0:
            if num == -66:
                c_other += 1
            else:
                c_bad += 1
                total_score += num
        elif num > 0:
            c_good += 1
            total_score += num
        
    total_score_avg=round(total_score/len(numbers),2)#应该加权平均
    ###
    sorted_numbers = numbers
    # 表格的大小设置
    cols = 10
    rows = int(len(numbers)/cols)+1
    cell_width = 70
    cell_height = 70  # 表格下方留出空间来放文字
    # 创建图像，大小为宽800px，高600px
    img_width = 700
    img_height = cell_height * rows + 100
    image = Image.new('RGB', (img_width, img_height), (255, 255, 255))  # 白色背景

    # 创建绘制对象
    draw = ImageDraw.Draw(image)
    numtoluck = {
        0: "普通",
        10: "大吉",
        9: "中吉",
        8: "小吉",
        7: "吉",
        6: "半吉",
        5: "末吉",
        4: "末小吉",
        -6: "凶",
        -7: "小凶",
        -8: "半凶",
        -9: "末凶",
        -10: "大凶",
        -66: "其他"
    }
    value_color_map = {
    10: "#1E3A5F",  # 深蓝色
    9: "#3A8EBA",    # 蓝色
    8: "#87CEEB",    # 浅蓝色
    7: "#ADD8E6",    # 淡蓝色
    6: "#B0C4DE",    # 淡蓝灰色
    5: "#B0E0E6",    # 灰蓝色
    4: "#B0E0E6",    # 灰蓝色
    0: "#D3D3D3",    # 灰色
    -6: "#FA8072",   # 淡红色
    -7: "#FA8072",   # 橙红色
    -8: "#FF4500",   # 红色
    -9: "#8B0000",   # 深红色
    -10: "#5A0000",  # 黑红色
    -66: "#800080",  # 紫色
}
    # 填充表格，使用排序后的颜色，并绘制数字
    font_path = {"yuppypath": Path(__file__).parent / "resource" / "font" / "sakura.ttf",}
    font_size = 20  # 设置字体大小
    font = ImageFont.truetype(str(font_path["yuppypath"]), font_size) 


    for i in range(rows):
        for j in range(cols):
            index = i * cols + j
            if index < len(sorted_numbers):
                value = sorted_numbers[index]
                color = value_color_map[value]
                # 计算表格单元格位置
                x0 = j * cell_width
                y0 = i * cell_height
                x1 = x0 + cell_width
                y1 = y0 + cell_height
                # 绘制矩形
                draw.rectangle([x0, y0, x1, y1], fill=color)
                # 绘制边框（黑色）
                border_color = (255, 255, 255)  # 黑色边框
                draw.rectangle([x0, y0, x1, y1], outline=border_color, width=2)

                # 获取数字的文本大小并计算居中位置
                text = numtoluck[value]
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                text_x = x0 + (cell_width - text_width) // 2  # 水平居中
                text_y = y0 + (cell_height - text_height) // 2  # 垂直居中
                if value<0:
                    text_color = (255, 255, 255)
                else:
                    text_color = (0, 0, 0)
                draw.text((text_x, text_y), text, font=font, fill=text_color)  # 白色文字
    # 添加自定义文字

    custom_text = f"吉类：{c_good}次 | 凶类：{c_bad}次 | 普通：{c_normal}次 | 其他：{c_other}次\n总平均：{total_score_avg}"


    # 使用 textbbox 来获取文字边界框
    bbox = draw.textbbox((0, 0), custom_text, font=font)
    text_width = bbox[2] - bbox[0]  # bbox 的宽度
    text_height = bbox[3] - bbox[1]  # bbox 的高度

    #text_x = (img_width - text_width) // 2  # 水平居中
    text_x = 30  # 水平居中
    text_y = img_height - text_height - 30  # 设置位置，距底部20px
    draw.text((text_x, text_y), custom_text, font=font, fill=(0, 0, 0))  # 黑色文字

    # 保存并显示图片
    output = BytesIO()
    image.save(output, format="png")
    return output
