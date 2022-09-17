"""Platform for IQtec cover integration."""
from __future__ import annotations

from typing import Any
import logging
import piqtec
import piqtec.devices
import piqtec.constants

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    DEVICE_CLASS_BLIND,
    SUPPORT_OPEN,
    SUPPORT_STOP,
    SUPPORT_CLOSE,
    SUPPORT_OPEN_TILT,
    SUPPORT_STOP_TILT,
    SUPPORT_CLOSE_TILT,
    SUPPORT_SET_POSITION,
    SUPPORT_SET_TILT_POSITION,
    ATTR_POSITION,
    ATTR_TILT_POSITION,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import (
    CONF_COVERS,
    CONF_ADDRESS,
    CONF_FRIENDLY_NAME
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from . import (
    DOMAIN,
    IQTEC_CONTROLLER,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Sets up IQtec cover"""

    if discovery_info is None:
        return

    coordinator = hass.data[DOMAIN][discovery_info[IQTEC_CONTROLLER]]
    controller = coordinator.controller
    add_entities(
        [IqtecCover(coordinator, controller, cover[CONF_ADDRESS], cover[CONF_FRIENDLY_NAME]) for cover in
         discovery_info[CONF_COVERS]]
    )


class IqtecCover(CoordinatorEntity, CoverEntity):
    """A cover implementation of IQtec sunblinds"""
    _attr_has_entity_name = True
    _address: str
    _cover: piqtec.devices.Sunblind

    _cover_position: int
    _tilt_position: int

    def __init__(self, coordinator: DataUpdateCoordinator, controller: piqtec.Controller, address: str,
                 name: str) -> None:
        super().__init__(coordinator)
        self.controller = controller
        self._name = name
        self._address = address
        self._connect()

    def _connect(self) -> None:
        self.controller.add_sunblind(self._address, self._name)

    @property
    def name(self):
        """Name of the entity"""
        return """IQtec Cover"""

    @property
    def current_cover_tilt_position(self) -> int:
        return self._tilt_position

    @property
    def current_cover_position(self) -> int:
        return self._cover_position

    @property
    def device_class(self) -> CoverDeviceClass:
        return DEVICE_CLASS_BLIND

    @property
    def supported_features(self) -> int:
        return SUPPORT_OPEN | SUPPORT_STOP | SUPPORT_CLOSE | SUPPORT_OPEN_TILT | SUPPORT_STOP_TILT | SUPPORT_CLOSE_TILT | SUPPORT_SET_POSITION | SUPPORT_SET_TILT_POSITION

    def open_cover(self, **kwargs: Any) -> None:
        self._cover.open()

    def close_cover(self, **kwargs: Any) -> None:
        self._cover.down()

    def set_cover_position(self, **kwargs: Any) -> None:
        hass_position = kwargs[ATTR_POSITION]
        self._cover.move(self.encode_position(hass_position))

    def stop_cover(self, **kwargs: Any) -> None:
        self._cover.stop()

    def open_cover_tilt(self, **kwargs: Any) -> None:
        self._cover.open()

    def close_cover_tilt(self, **kwargs: Any) -> None:
        self._cover.tilt(piqtec.constants.SUNBLIND_FULL_TILT)

    def set_cover_tilt_position(self, **kwargs: Any) -> None:
        hass_tilt = kwargs[ATTR_TILT_POSITION]
        self._cover.tilt(self.encode_tilt(hass_tilt))

    def stop_cover_tilt(self, **kwargs: Any) -> None:
        self._cover.stop()

    @staticmethod
    def encode_tilt(hass_tilt: int):
        return int((100 - hass_tilt) * piqtec.constants.SUNBLIND_FULL_TILT / 100)

    @staticmethod
    def decode_tilt(iqtec_tilt: int):
        return 100 - int(iqtec_tilt / piqtec.constants.SUNBLIND_FULL_TILT * 100)

    @staticmethod
    def encode_position(has_pos: int) -> int:
        return int((100 - has_pos) * 10)

    @staticmethod
    def decode_position(iqtec_pos: int) -> int:
        return 100 - int(iqtec_pos / 10)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._cover_position = self._cover.position
        self._tilt_position = self._cover.rotation
        self.async_write_ha_state()
