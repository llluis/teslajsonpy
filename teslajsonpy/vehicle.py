#  SPDX-License-Identifier: Apache-2.0
"""
Python Package for controlling Tesla API.

For more details about this api, please refer to the documentation at
https://github.com/zabuldon/teslajsonpy
"""
import logging

_LOGGER = logging.getLogger(__name__)


class VehicleDevice:
    """Home-assistant class of Tesla vehicles.

    This is intended to be partially inherited by a Home-Assitant entity.
    """

    def __init__(self, data, controller):
        """Initialize the Vehicle.

        Parameters
        ----------
        data : dict
            The base state for a Tesla vehicle.
            https://tesla-api.timdorr.com/vehicle/state/data
        controller : teslajsonpy.Controller
            The controller that controls updates to the Tesla API.

        Returns
        -------
        None

        """
        self._id = data["id"]
        self._vehicle_id = data["vehicle_id"]
        self._display_name = data["display_name"]
        self._vin = data["vin"]
        self._state = data["state"]
        self._car_type = f"Model {str(self._vin[3]).upper()}"
        self._car_version = ""
        self.attrs = {}
        self._controller = controller
        self.should_poll = True
        self.type = "device"

    def _name(self):
        return (
            "{} {}".format(self._display_name, self.type)
            if self._display_name is not None and self._display_name != self._vin[-6:]
            else "Tesla Model {} {}".format(str(self._vin[3]).upper(), self.type)
        )

    def _uniq_name(self):
        return "Tesla Model {} {} {}".format(
            str(self._vin[3]).upper(), self._vin[-6:], self.type
        )

    def id(self):
        # pylint: disable=invalid-name
        """Return the id of this Vehicle."""
        return self._id

    def car_name(self):
        """Return the car name of this Vehicle."""
        return (
            self._display_name
            if self._display_name is not None and self._display_name != self._vin[-6:]
            else f"Tesla Model {str(self._vin[3]).upper()}"
        )

    @property
    def car_version(self):
        """Return the software version of this Vehicle."""
        return self._car_version

    @property
    def car_type(self):
        """Return the type of this Vehicle."""
        return self._car_type

    def assumed_state(self):
        # pylint: disable=protected-access
        """Return whether the data is from an online vehicle."""
        return not self._controller.car_online[self.id()] and (
            self._controller._last_update_time[self.id()]
            - self._controller._last_wake_up_time[self.id()]
            > self._controller.update_interval
        )

    async def async_update(self):
        """Update the car version."""
        await self._controller.update(self.id(), wake_if_asleep=False)
        state = self._controller.get_state_params(self.id())
        if state and "car_version" in state:
            self._car_version = state["car_version"]

    @staticmethod
    def is_armable():
        """Return whether the data is from an online vehicle."""
        return False

    @staticmethod
    def is_armed():
        """Return whether the vehicle is armed."""
        return False