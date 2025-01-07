import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

#初始化bot
nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)

#数据库方法
from neribot.services.db_context import init, disconnect
driver.on_startup(init)
driver.on_shutdown(disconnect)

#加载插件
nonebot.load_plugins("neribot/main_plugins")
nonebot.load_plugins("neribot/plugins")
nonebot.load_plugins("neribot/privacy_plugins")

if __name__ == "__main__":
    nonebot.run()
