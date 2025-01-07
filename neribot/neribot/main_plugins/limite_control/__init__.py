import time
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from collections import deque
from nonebot.log import logger


from neribot.models.ban_model import BanConsole



class IntTrigger:
    def __init__(self, T_during, T_times):
        """
        初始化类的实例。
        
        :param T_TIME: 时间窗口的大小（秒）
        :param T_times: 触发的次数
        """
        self.T_TIME = T_during  # 时间窗口大小，单位为秒
        self.T_times = T_times  # 触发次数
        self.records = deque()  # 用来存储整数及其时间戳

    def _cleanup(self, current_time):
        """
        清理掉超过时间窗口的记录。
        
        :param current_time: 当前时间
        """
        while self.records and self.records[0][1] <= current_time - self.T_TIME:
            self.records.popleft()

    def add_int(self, num):
        """
        接收到一个整数，如果该整数在指定时间窗口内出现次数达到指定次数，则返回该整数。
        
        :param num: 需要添加的整数
        :return: 返回整数，如果条件满足
        """
        current_time = time.time()  # 获取当前时间戳
        self._cleanup(current_time)  # 清理过时的记录
        
        # 将当前整数和时间戳添加到记录队列
        self.records.append((num, current_time))
        
        # 统计队列中与当前整数相同的记录
        count = sum(1 for x in self.records if x[0] == num)
        
        # 如果在时间窗口内出现次数达到指定的次数，返回真，否则返回假
        if count >= self.T_times:
            return True
        return False

trigger = IntTrigger(T_during=2, T_times=6) #T_during内触发了T_times就返回特定值
# 恶意触发命令检测
@run_preprocessor #需要实行恶意触发检测的插件优先级应该设置为[5-10]闭区间
async def _(matcher: Matcher, event: GroupMessageEvent):
    if matcher.priority > 10 or matcher.priority<5:
        return
    user_id = getattr(event, "user_id", None)
    is_over = trigger.add_int(num = int(user_id))
    if is_over:
        logger.warning(f"恶意触发用户：{user_id}")
        if not await BanConsole.is_ban(str(user_id)): #如果恶意触发了，但还没被ban，那么就ban
            await BanConsole.ban(str(user_id), 1800) #ban多久（秒