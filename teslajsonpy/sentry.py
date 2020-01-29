#  SPDX-License-Identifier: Apache-2.0
"""
Python Package for controlling Tesla API.

For more details about this api, please refer to the documentation at
https://github.com/zabuldon/teslajsonpy
"""
import time

from teslajsonpy.vehicle import VehicleDevice


class SentrySwitch(VehicleDevice):
    """Home-Assistant class for the sentry mode of a Tesla VehicleDevice."""

    def __init__(self, data, controller):
        """Initialize the Sentry Mode Switch.

        Parameters
        ----------
        data : dict
            The base state for a Tesla vehicle.
            https://tesla-api.timdorr.com/vehicle/commands/sentrymode
        controller : teslajsonpy.Controller
            The controller that controls updates to the Tesla API.

        Returns
        -------
        None

        """
        super().__init__(data, controller)
        self.__manual_update_time = 0
        self.__sentry_state = False
        self.type = "sentry switch"
        self.hass_type = "switch"
        self.name = self._name()
        self.uniq_name = self._uniq_name()

    async def async_update(self):
        """Update the vehicle state of the Tesla Vehicle."""
        await super().async_update()
        last_update = self._controller.get_last_update_time(self._id)
        if last_update >= self.__manual_update_time:
            data = self._controller.get_state_params(self._id)
            self.__sentry_state = (data and data["sentry_mode"])

    async def enable_sentry(self):
        """Enable the Tesla Vehicle Sentry Mode."""
        if not self.__sentry_state:
            data = await self._controller.command(
                self._id, 
                "set_sentry_mode", 
                {"on": True},
                wake_if_asleep=True
            )
            if data and data["response"]["result"]:
                self.__sentry_state = True
            self.__manual_update_time = time.time()

    async def disable_sentry(self):
        """Disable the Tesla Vehicle Sentry Mode."""
        if self.__sentry_state:
            data = await self._controller.command(
                self._id, 
                "set_sentry_mode", 
                {"on": False},
                wake_if_asleep=True
            )
            if data and data["response"]["result"]:
                self.__sentry_state = False
            self.__manual_update_time = time.time()

    def get_value(self):
        """Return whether the Tesla Sentry Mode is enabled."""
        return self.__sentry_state

    @staticmethod
    def has_battery():
        """Return whether the Tesla charger has a battery."""
        return False
