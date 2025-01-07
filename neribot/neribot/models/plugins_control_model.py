from tortoise import fields
from neribot.services.db_context import Model


class PluginsGroupControl(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    group_id = fields.CharField(255, null=True)
    """群id"""
    main_switch = fields.IntField(default=1) #值为0关闭
    """总开关"""
    enable_plugins = fields.JSONField(default=[])
    """开启的插件"""
    group_name = fields.CharField(255, null=True)
    """群名"""
    class Meta:  # type: ignore
        table = "plugins_control"
        table_description = "插件控制表"
    
    @classmethod
    async def custom_get_or_create(cls, group_id: str):
        group = await cls.filter(group_id=group_id).first()
        if group is None:
            group = await cls.create(group_id=group_id)
        return group, None

    @classmethod
    async def is_plugin_enable(cls, group_id: str, plugin_name: str) -> bool:
        """判断插件是否打开
        参数:
            group_id: 用户id
            plugin_name: 插件名
        返回:
            bool: 是否打开
        """
        group, _ = await cls.custom_get_or_create(group_id=group_id)
        main_switch = group.main_switch
        is_plugin_name_enabled = True if plugin_name in group.enable_plugins else False
        return main_switch and is_plugin_name_enabled #总开关和插件开关都打开才返回True
    
    @classmethod
    async def is_main_switch_on(cls, group_id: str) -> bool:
        """判断群聊总开关是否打开
        参数:
            group_id: 用户id
        返回:
            bool: 是否打开
        """
        group, _ = await cls.custom_get_or_create(group_id=group_id)
        if group.main_switch == 0:
            return False
        else:
            return True
    @classmethod
    async def get_enable_plugins(cls, group_id: str) -> bool:
        """获取开启的插件
        参数:
            group_id: 用户id
        返回:
            bool: 是否打开
        """
        group, _ = await cls.custom_get_or_create(group_id=group_id)
        return group.enable_plugins

    @classmethod
    async def update_main_switch(cls, group_id: str, switch_bool: int) -> bool:
        """更新群聊总开关
        参数:
            group_id: 用户id
            switch_bool: 1为开，0为关
        """
        group, _ = await cls.custom_get_or_create(group_id=group_id)
        group.main_switch = switch_bool
        await group.save(update_fields=["main_switch"])

    @classmethod
    async def update_enable_plugins(cls, group_id: str, plugins_list: list) -> bool:
        """将插件启用情况更新
        参数:
            group_id: 用户id
            plugins_list: 插件列表
        返回:
            bool: 是否被ban
        """
        group, _ = await cls.custom_get_or_create(group_id=group_id)
        group.enable_plugins = plugins_list
        await group.save(update_fields=["enable_plugins"])
    
    @classmethod
    async def _run_script(cls):
        return [
            "ALTER TABLE plugins_control ADD CONSTRAINT unique_group_id UNIQUE (group_id);"
        ]
    