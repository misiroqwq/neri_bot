import time
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
)
from nonebot_plugin_session import EventSession

from neribot.configs.config import Plugin_Rule, ADMIN_GROUP

class RateLimiter: #超过了返回true，没超过返回false
    def __init__(self, limit, window):
        # 限制请求次数 (limit) 和时间窗口 (window)
        self.limit = limit
        self.window = window
        self.requests = []

    def is_allowed(self, current_time):
        # 移除过期的请求（超出时间窗口的请求）
        self.requests = [req_time for req_time in self.requests if current_time - req_time <= self.window]
        
        # 检查当前请求是否超过限制
        if len(self.requests) >= self.limit:
            self.requests.append(current_time)
            return True
        else:
            # 记录当前请求的时间
            self.requests.append(current_time)
            return False
# 创建 RateLimiter 实例，限制每60秒内最多4个请求
rate_limiter = RateLimiter(limit=3, window=100)

# 群员增加处理
group_increase_handle = on_notice(priority=1, block=False)
# 群员减少处理
group_decrease_handle = on_notice(priority=1, block=False)

@group_increase_handle.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.user_id == int(bot.self_id):
        groupinfo = await bot.get_group_info(group_id = int(event.group_id))
        group_name = groupinfo["group_name"]
        await bot.send_group_msg(group_id = ADMIN_GROUP, message = f"进入群聊：{group_name} ({event.group_id})")


@group_decrease_handle.handle()
async def _(bot: Bot, session: EventSession, event: GroupDecreaseNoticeEvent):
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    user_info_dict = await bot.get_group_member_info(user_id=int(user_id), group_id=int(group_id))
    user_name = user_info_dict["card"] or user_info_dict["nickname"]
    #群组控制
    is_group_notice = await Plugin_Rule.get_rule(plugin_name = "group_decrease_notice", session = session, check_user = False)
    
    if event.sub_type == "kick_me":
        """踢出Bot"""
        groupinfo = await bot.get_group_info(group_id = group_id)
        try:
            group_name = groupinfo["group_name"]
        except KeyError:
            group_name = group_id
        await bot.send_group_msg(group_id = ADMIN_GROUP, message = f"被群聊：{group_name} ({event.group_id}) 踢出")
    elif event.sub_type == "kick" and is_group_notice:
        is_over_frequency = rate_limiter.is_allowed(time.time()) #频率控制
        if not is_over_frequency:
            operator = await bot.get_group_member_info(user_id=int(event.operator_id), group_id=int(group_id))
            operator_name = operator["card"] or operator["nickname"]
            await bot.send_group_msg(group_id = group_id, message = f"{user_name} ({user_id}) 被 {operator_name} 送走了.")
    elif event.sub_type == "leave" and is_group_notice:
        await bot.send_group_msg(group_id = group_id, message = f"{user_name} ({user_id}) 离开了我们...")
