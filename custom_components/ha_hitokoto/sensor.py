from datetime import timedelta
import aiohttp
import async_timeout
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_PATH

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Hitokoto sensor from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HitokotoSensor(coordinator, entry)])

    # 监听配置变化
    entry.async_on_unload(
        entry.add_update_listener(_async_update_listener)
    )

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """处理配置更新."""
    await hass.config_entries.async_reload(entry.entry_id)

class HitokotoCoordinator(DataUpdateCoordinator):
    """通用的 API 请求协调器，支持动态 URL 和分类参数"""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        self._session = None

        interval = timedelta(seconds=entry.options.get("update_interval", 3600))
        super().__init__(
            hass,
            _LOGGER,
            name="Hitokoto 一言",
            update_method=self._async_fetch,
            update_interval=interval,
        )

    async def _async_fetch(self):
        """从 API 获取数据，失败时抛出 UpdateFailed"""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        base_url = self.entry.options.get("api_url", "").rstrip("/")
        if not base_url:
            raise UpdateFailed("未配置 API 地址")
        url = f"{base_url}{API_PATH}"

        params = {}
        category = self.entry.options.get("category", "").strip()
        if category:
            params["category"] = category

        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, params=params) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"API 返回错误状态码: {resp.status}")
                    data = await resp.json()
                    if "hitokoto" not in data:
                        raise UpdateFailed("API 返回数据缺少 'hitokoto' 字段")
                    return data
        except Exception as err:
            raise UpdateFailed(f"请求失败: {err}") from err

    async def close_session(self):
        """关闭 aiohttp 会话"""
        if self._session:
            await self._session.close()
            self._session = None

class HitokotoSensor(SensorEntity):
    """显示一言的传感器实体"""

    def __init__(self, coordinator: HitokotoCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}"
        self._attr_name = "Hitokoto 一言"

    @property
    def native_value(self):
        return self.coordinator.data.get("hitokoto") if self.coordinator.data else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "author": data.get("author"),
            "categories": data.get("categories"),
            "commit_from": data.get("commit_from"),
            "created_at": data.get("created_at"),
            "length": data.get("length"),
            "id": data.get("id"),
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )