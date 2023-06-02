import logging
from homeassistant.components.switch import SwitchEntity
from .client import Client

from .const import (
    DOMAIN,
    DEFAULT_ACCESS_ID_FOR_ON,
    DEFAULT_ACCESS_NAME_FOR_ON,
    DEFAULT_ACCESS_NAME_FOR_OFF,    
    ACCESS_NAME_FOR_OFF_OVERRIDE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    client: Client = hass.data[DOMAIN][config_entry.entry_id]
    data = await hass.async_add_executor_job(client.update_data)

    proxy_hosts_access_id_map = data.get('proxy_hosts_access_id_map', {})
    proxy_hosts_id_map = data.get('proxy_hosts_id_map', {})
    access_map = data.get('access_map', {})
    switchs = []
    for name, access_id in proxy_hosts_access_id_map.items():
        on_id = DEFAULT_ACCESS_ID_FOR_ON
        if DEFAULT_ACCESS_NAME_FOR_ON:
            on_id = access_map.get(DEFAULT_ACCESS_NAME_FOR_ON, DEFAULT_ACCESS_ID_FOR_ON)
        off_name = ACCESS_NAME_FOR_OFF_OVERRIDE.get(name, DEFAULT_ACCESS_NAME_FOR_OFF)
        off_id = access_map.get(off_name)
        proxy_host_id = proxy_hosts_id_map.get(name)
        switchs.append(AccessSwitch(name, client, proxy_host_id, on_id, off_id))
    # 将自定义实体添加到 Home Assistant 中
    async_add_entities(switchs, True)

    # 更新实体数量
    config_entry.add_update_listener(update_listener)

    return True

async def update_listener(hass, entry):
    # 获取实体数量
    entity_count = len(hass.data[DOMAIN]["entities"])

    # 更新实体数量
    entry.data["entity_count"] = entity_count
    hass.config_entries.async_update_entry(entry)

class AccessSwitch(SwitchEntity):
    def __init__(self, name, client, id, on_id, off_id):
        self._name = name
        self.client = client
        self.id = id
        self.on_id = on_id
        self.off_id = off_id
        
    def update(self) -> None:
        self.client.update_data()

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self.client.data.get('proxy_hosts_access_id_map', {}).get(self.name) == self.on_id

    def turn_on(self, **kwargs):
        # Code to turn on the switch
        # self._state = True
        resdata = self.client.put_host_access_id(self.id, self.on_id)
        if resdata.get('access_list_id') == self.on_id:
            self.client.data['proxy_hosts_access_id_map'][self.name] = self.on_id
            self.async_update_ha_state()

    def turn_off(self, **kwargs):
        # Code to turn off the switch
        resdata = self.client.put_host_access_id(self.id, self.off_id)
        if resdata.get('access_list_id') == self.off_id:
            self.client.data['proxy_hosts_access_id_map'][self.name] = self.off_id
            self.async_update_ha_state()