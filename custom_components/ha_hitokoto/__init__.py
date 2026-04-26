from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS
from .config_flow import HitokotoOptionsFlowHandler
from .sensor import HitokotoCoordinator, HitokotoSensor

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hitokoto from a config entry."""
    if not entry.options:
        hass.config_entries.async_update_entry(
            entry,
            options={"api_url": "https://v1.hitokoto.cn", "category": "", "update_interval": 3600}
        )

    # 创建协调器并存储
    coordinator = HitokotoCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # 转发到传感器平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and close session."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator:
        await coordinator.close_session()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

def async_get_options_flow(config_entry):
    """获取选项流."""
    return HitokotoOptionsFlowHandler(config_entry)