#  SPDX-License-Identifier: Apache-2.0
"""
Python Package for controlling Tesla API.

For more details about this api, please refer to the documentation at
https://github.com/zabuldon/teslajsonpy
"""
from typing import Dict, Optional, Text

from teslajsonpy.vehicle import VehicleDevice


class Battery(VehicleDevice):
    """Home-Assistant battery class for a Tesla VehicleDevice."""

    def __init__(self, data: Dict, controller) -> None:
        """Initialize the Battery sensor.

        Args:
            data (Dict): The charging parameters for a Tesla vehicle.
            https://tesla-api.timdorr.com/vehicle/state/chargestate
            controller (Controller): The controller that controls updates to the Tesla API.

        """
        super().__init__(data, controller)
        self.__battery_level: int = 0
        self.__usable_battery_level: int = 0
        self.__charging_state: bool = None
        self.__charge_port_door_open: bool = None
        self.type: Text = "battery sensor"
        self.measurement: Text = "%"
        self.hass_type: Text = "sensor"
        self._device_class: Text = "battery"
        self.name: Text = self._name()
        self.uniq_name: Text = self._uniq_name()
        self.bin_type: hex = 0x5

    async def async_update(self) -> None:
        """Update the battery state."""
        await super().async_update()
        data = self._controller.get_charging_params(self._id)
        if data:
            self.__battery_level = data["battery_level"]
            self.__usable_battery_level = data["usable_battery_level"]
            self.__charging_state = data["charging_state"] == "Charging"

    @staticmethod
    def has_battery() -> bool:
        """Return whether the device has a battery."""
        return True

    def get_value(self) -> int:
        """Return the battery level."""
        return self.__battery_level

    def get_usable_value(self) -> int:
        """Return the usable battery level."""
        return self.__usable_battery_level

    def battery_level(self) -> int:
        """Return the battery level."""
        return self.get_value()

    def battery_charging(self) -> bool:
        """Return the battery level."""
        return self.__charging_state

    @property
    def device_class(self) -> Text:
        """Return the HA device class."""
        return self._device_class


class Range(VehicleDevice):
    """Home-Assistant class of the battery range for a Tesla VehicleDevice."""

    def __init__(self, data: Dict, controller) -> None:
        """Initialize the Battery range sensor.

        Parameters
        ----------
        data : dict
            The charging parameters for a Tesla vehicle.
            https://tesla-api.timdorr.com/vehicle/state/chargestate
        controller : teslajsonpy.Controller
            The controller that controls updates to the Tesla API.

        Returns
        -------
        None

        """
        super().__init__(data, controller)
        self.__battery_range = 0
        self.__est_battery_range = 0
        self.__ideal_battery_range = 0
        self.type = "range sensor"
        self.__rated = True
        self.measurement = "LENGTH_MILES"
        self.hass_type = "sensor"
        self._device_class: Optional[Text] = None
        self.name = self._name()
        self.uniq_name = self._uniq_name()
        self.bin_type = 0xA

    async def async_update(self):
        """Update the battery range state."""
        await super().async_update()
        data = self._controller.get_charging_params(self._id)
        if data:
            self.__battery_range = data["battery_range"]
            self.__est_battery_range = data["est_battery_range"]
            self.__ideal_battery_range = data["ideal_battery_range"]
        data = self._controller.get_gui_params(self._id)
        if data:
            if data["gui_distance_units"] == "mi/hr":
                self.measurement = "LENGTH_MILES"
            else:
                self.measurement = "LENGTH_KILOMETERS"
            self.__rated = data["gui_range_display"] == "Rated"

    @staticmethod
    def has_battery():
        """Return whether the device has a battery."""
        return False

    def get_value(self):
        """Return the battery range.

        This function will return either the rated range or the ideal range
        based on the gui_settings.
        """
        if self.__rated:
            return self.__battery_range
        return self.__ideal_battery_range

    @property
    def device_class(self) -> Text:
        """Return the HA device class."""
        return self._device_class
