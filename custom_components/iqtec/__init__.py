"""IQtec Home integration."""
from __future__ import annotations

import logging
import voluptuous as vol
import piqtec
import piqtec.exceptions
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import discovery
from homeassistant.const import (
    Platform,
    CONF_FRIENDLY_NAME,
    CONF_HOST,
    CONF_ADDRESS,
    CONF_COVERS,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

DOMAIN = 'iqtec'
PLATFORMS = [Platform.COVER, ]
IQTEC_CONTROLLER = 'controller'

_LOGGER = logging.getLogger(__name__)

COVER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME, default='iqtec_sunblind'): cv.string,
    }
)

CONTROLLER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME, default='iqtec_controller'): cv.string,
        vol.Optional(CONF_COVERS): vol.Schema(vol.All(cv.ensure_list, [COVER_SCHEMA]))
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(vol.All(cv.ensure_list, [CONTROLLER_SCHEMA]))
    }
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup the IQtec component."""
    hass.data[DOMAIN] = []

    success = False
    for controller_config in config[DOMAIN]:
        success = success or _setup_controller(hass, controller_config, config)

    return success


def _setup_controller(hass: HomeAssistant, controller_config: ConfigType, config: ConfigType) -> bool:
    """Sets up IQtec API connection"""
    host = controller_config[CONF_HOST]
    name = controller_config[CONF_FRIENDLY_NAME]
    position = len(hass.data[DOMAIN])

    controller = piqtec.Controller(host, name)
    # TODO add a connection check
    try:
        pass
    except Exception as e:
        _LOGGER.error(f"Unable to setup controller {host}: {e}")
        return False
    coordinator = UpdateCoordinator(controller)
    hass.data[DOMAIN].append(coordinator)
    _LOGGER.debug(f"IQtec controller {host} is set to: {position}")

    for platform in PLATFORMS:
        discovery.load_platform(
            hass,
            platform,
            DOMAIN,
            {IQTEC_CONTROLLER: position, **controller_config},
            config
        )

    return True


class UpdateCoordinator(DataUpdateCoordinator):
    """IQtec Data Update coordinator"""

    def __init__(self, hass: HomeAssistant, controller: piqtec.Controller):
        super().__init__(
            hass,
            _LOGGER,
            name=controller.name,
            update_interval=timedelta(seconds=1)
        )
        self.controller = controller

    async def _async_update_data(self):
        try:
            self.controller.update()
        except piqtec.exceptions.APIError as e:
            raise UpdateFailed(f"Error while communicating with API: {e}")

