import logging
import math
import struct

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.const import STATE_UNKNOWN

from .const import (ATTRIBUTION, ATTR_ATTRIBUTION, DOMAIN, SENSOR_TYPES, MEASURE_VPD, MEASURE_HUMIDITY,
                    CONF_MODEL, MODEL, SENSORS_BY_MODEL, MODEL_WAVE_PLUS,
                    MIN_TIME_BETWEEN_UPDATES, CONF_MAC, UNIT_SYSTEMS, CONF_UNIT_SYSTEM, UNIT_SYSTEM_IMPERIAL)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_MODEL, default=MODEL_WAVE_PLUS):
                vol.In(SENSORS_BY_MODEL.keys()),
    vol.Optional(CONF_UNIT_SYSTEM, default=UNIT_SYSTEM_METRIC):
                vol.In(UNIT_SYSTEMS.keys())
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    reader = None
    model = config.get(CONF_MODEL)
    if model == MODEL_WAVE_PLUS:
        reader = AirthingsWavePlusDataReader(config.get(CONF_MAC))
    else:
        reader = AirthingsWaveDataReader(config.get(CONF_MAC))

    unit_system = config.get(CONF_UNIT_SYSTEM)
    _LOGGER.debug(f"Using unit system '{unit_system}' for Airthings model '{model}'")

    sensors = []
    for key in SENSORS_BY_MODEL[model]:
        [name, icon, device_class] = SENSOR_TYPES[key]
        unit = UNIT_SYSTEMS[unit_system].get(key)
        sensors.append(AirthingsSensorEntity(reader, key, name, unit, icon, device_class))
    add_devices(sensors)


class AirthingsWavePlusDataReader:
    def __init__(self, mac):
        self._mac = mac
        self._state = {}

    def get_data(self, key):
        if key in self._state:
            return self._state[key]
        return STATE_UNKNOWN

    @property
    def mac(self):
        return self._mac

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        _LOGGER.debug(f"Updating data from Airthings Wave {self._mac}")

        import pygatt
        from pygatt.backends import Characteristic
        adapter = pygatt.backends.GATTToolBackend()
        # char = 'b42e2a68-ade7-11e4-89d3-123b93f75cba'

        try:
            # reset_on_start must be false - reset is hardcoded to execute sudo, which doesn't exist
            # in the hass.io Docker container.
            adapter.start(reset_on_start=False)
            device = adapter.connect(self._mac)

            # Unclear why this does not work. Seems broken in the command line tool too. Hopefully handle is stable...
            # value = device.char_read(char,timeout=10)
            value = device.char_read_handle('0x000d', timeout=10)
            (humidity, light, sh_rad, lo_rad, temp, pressure,
             co2, voc) = struct.unpack('<xbxbHHHHHHxxxx', value)

            self._state[MEASURE_HUMIDITY] = humidity / 2.0
            self._state['light'] = light * 1.0
            self._state['short_radon'] = sh_rad
            self._state['long_radon'] = lo_rad
            self._state['temperature'] = temp / 100.0
            self._state['pressure'] = pressure / 50.0
            self._state['co2'] = co2 * 1.0
            self._state['voc'] = voc * 1.0

            temp_celsius = temp  # FIXME: assumed Celsius

            # calculate vapor pressure deficit
            saturation_vapor_pressure = 0.6108 * \
                exp(17.27 * temp_celsius / (temp_celsius + 237.3))
            actual_vapor_pressure = humidity / 100 * saturation_vapor_pressure
            vapor_pressure_deficit = actual_vapor_pressure - saturation_vapor_pressure
            self._state[MEASURE_VPD] = vapor_pressure_deficit

        finally:
            adapter.stop()

class AirthingsWaveDataReader:
    def __init__(self, mac):
        self._mac = mac
        self._state = {}

    def get_data(self, key):
        if key in self._state:
            return self._state[key]
        return STATE_UNKNOWN

    @property
    def mac(self):
        return self._mac

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        _LOGGER.debug(f"Updating data from Airthings Wave {self._mac}")

        import pygatt
        from pygatt.backends import Characteristic
        adapter = pygatt.backends.GATTToolBackend()
        # char = 'b42e2a68-ade7-11e4-89d3-123b93f75cba'

        try:
            # reset_on_start must be false - reset is hardcoded to execute sudo, which doesn't exist
            # in the hass.io Docker container.
            adapter.start(reset_on_start=False)
            device = adapter.connect(self._mac)

            # Unclear why this does not work. Seems broken in the command line tool too. Hopefully handle is stable...
            # value = device.char_read(char,timeout=10)
            value = device.char_read_handle('0x000d', timeout=10)

            data = struct.unpack('<4B8H', value)
            humidity = self._state['humidity'] = data[1] / 2.0
            self._state['short_radon'] = round(data[4] / 37, 2)
            self._state['long_radon'] = round(data[5] / 37, 2)
            self._state['temperature'] = data[6] / 100.0

            temp_celsius = self._state['temperature']  # FIXME: assumed Celsius

            # calculate vapor pressure deficit
            saturation_vapor_pressure = 0.6108 * \
                exp(17.27 * temp_celsius / (temp_celsius + 237.3))
            actual_vapor_pressure = humidity / 100 * saturation_vapor_pressure
            vapor_pressure_deficit = actual_vapor_pressure - saturation_vapor_pressure
            self._state[MEASURE_VPD] = vapor_pressure_deficit

        finally:
            adapter.stop()




class AirthingsSensorEntity(Entity):
    """Representation of a Sensor."""

    def __init__(self, reader, key, name, unit, icon, device_class):
        """Initialize the sensor."""
        self._reader = reader
        self._key = key
        self._name = name
        self._unit = unit
        self._icon = icon
        self._device_class = device_class

        self._attrs = {
            ATTR_ATTRIBUTION: ATTRIBUTION
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Airthings Wave {}'.format(self._name)

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def device_class(self):
        """Return the icon of the sensor."""
        return self._device_class

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._reader.get_data(self._key)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def unique_id(self):
        return '{}-{}'.format(self._reader.mac, self._name)

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._reader.update()

   @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs
