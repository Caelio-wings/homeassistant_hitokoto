from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_API_BASE_URL

UPDATE_INTERVALS = {
    300: "5分钟",
    900: "15分钟",
    1800: "30分钟",
    3600: "1小时",
    7200: "2小时",
    21600: "6小时",
    43200: "12小时",
    86400: "1天"
}

def get_options_schema(current: dict = None):
    """生成配置/选项的 schema，避免重复代码"""
    if current is None:
        current = {}
    return vol.Schema({
        vol.Required("api_url", default=current.get("api_url", DEFAULT_API_BASE_URL)): str,
        vol.Optional("category", default=current.get("category", "")): str,
        vol.Optional("update_interval", default=current.get("update_interval", 3600)): vol.In(UPDATE_INTERVALS),
    })

class HitokotoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """配置流"""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Hitokoto 一言",
                data={},
                options=user_input
            )
        return self.async_show_form(step_id="user", data_schema=get_options_schema())

class HitokotoOptionsFlowHandler(config_entries.OptionsFlow):
    """选项流"""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options or {}
        return self.async_show_form(step_id="init", data_schema=get_options_schema(current))