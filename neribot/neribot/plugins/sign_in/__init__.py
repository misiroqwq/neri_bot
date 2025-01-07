import random
import textwrap
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from nonebot.log import logger
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
)
from nonebot.params import CommandArg
import os
from datetime import datetime
import pytz
import re
from .utils import group_checking_rank, get_user_card, get_user_avatar, get_user_id_list, image_b64
from .config import text_neri
from .sign_user import SignUser
from nonebot_plugin_session import EventSession
from neribot.configs.config import Plugin_Rule

async def rule(session: EventSession) -> bool:
    return await Plugin_Rule.get_rule(plugin_name = "sign", session = session)


sign_plugin = on_command("签到", aliases={"打卡"}, priority=5, block=True, rule=rule)
@sign_plugin.handle()
async def _(event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()):
    cmd_arg = arg.extract_plain_text().strip()

    if "排行" in cmd_arg or "排名" in cmd_arg:
        all_rank = True if "总" in cmd_arg else False
        num = 10
        num_match = re.search(r'[0-9]+', cmd_arg)
        if num_match:
            num = int(num_match.group(0))
            num = max(10, min(num, 50))  # 保证 num 在 [10, 50] 之间

        _image = await group_checking_rank(bot, str(event.group_id), num, all_rank)
        if _image:
            if _image == "当前还没有人签到过哦...":
                await sign_plugin.finish(_image)
            await sign_plugin.finish(await image_b64(b64=_image.pic2bs4()))
        else:
            await sign_plugin.finish("生成签到排行错误")
    # 获取用户
    user = await SignUser.get_user(user_id=str(event.user_id))
    if user:
        if user.checkin_time_last == str(datetime.now().strftime("%Y%m%d")):
            await sign_plugin.finish('今天已经签到过啦，明天再来叭~', at_sender=True)

    # 执行签到
    await SignUser.sign(event.user_id)

    # 获取：用户，昵称，头像，签到次数
    user = await SignUser.get_user(user_id=str(event.user_id))
    nickname = await get_user_card(bot, event.group_id, event.user_id)
    avatar = BytesIO(await get_user_avatar(event.user_id, 640))
    checkin_count = user.checkin_count

    # 计算签到天数排行
    member_list = await get_user_id_list(bot=bot, group_id=str(event.group_id))
    rank = await SignUser.get_checkin_count_rank(rank_user = str(event.user_id), member_list = member_list)

    # 随机语录文本
    response_text = random.choice(text_neri)

    # 背景图案
    sign_bg_list = os.listdir(os.path.dirname(os.path.abspath(__file__)) + "/image/sign_bg")
    sign_bg = Image.open(os.path.dirname(os.path.abspath(__file__)) + f"/image/sign_bg/{random.choice(sign_bg_list)}")
    draw = ImageDraw.Draw(sign_bg)

    # 调整样式
    stamp_img = Image.open(avatar)
    stamp_img = stamp_img.resize((502, 502))
    w, h = stamp_img.size
    mask = Image.new('RGBA', (w, h), color=(0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, w, h), fill=(0, 0, 0, 255))
    sign_bg.paste(stamp_img, (208, 43, 208+w, 43+h), mask)

    # 绘制文字
    font_path = os.path.dirname(os.path.abspath(__file__)) + "/STHUPO.TTF"
    with open(font_path, "rb") as draw_font:
        bytes_font = BytesIO(draw_font.read())
        text_font = ImageFont.truetype(font=bytes_font, size=45)

    draw.text(xy=(98, 580), text=f"欢迎回来, {nickname}~!", font=text_font)
    draw.text(xy=(98, 633), text=f"累计签到 {checkin_count} 天", font=text_font)
    draw.text(xy=(98, 686), text=f"当前群排名: 第 {rank} 位", fill=(200, 255, 255), font=text_font)
    para = textwrap.wrap(f"{response_text}", width=16)
    for i, line in enumerate(para):
        draw.text((98, 53 * i + 845), line, 'white', text_font)

    output = BytesIO()
    sign_bg.save(output, format="png")
    
    await sign_plugin.send(MessageSegment.image(output))

