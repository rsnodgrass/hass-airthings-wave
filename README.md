# Airthings Wave Air Quality for Home Assistant

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![beta_badge](https://img.shields.io/badge/maturity-Beta-yellow.png)

Home Assistant support for the [Airthing Wave](https://smile.amazon.com/Airthings-Wave-Generation-Easy-Use/dp/B07WWV7K3K?tag=rynoshark-20) and [Airthings Wave Plus](https://smile.amazon.com/Airthings-2930-Quality-Detection-Dashboard/dp/B07JB8QWH6?tag=rynoshark-20) indoor air quality sensors.

**SEE https://github.com/custom-components/sensor.airthings_wave for a sensor that appears to support Wave Plus now**

## Support

**Beware, very untested.**

This was developed by [@gkreitz](https://github.com/gkreitz/homeassistant-airthings) and [@mstanislav](https://github.com/mstanislav/homeassistant-airthings).

From @gkreitz: *I wanted something to read my Airthings Wave Plus, so I built this. Far from production quality. Magic hardcoded constants. Reads data the wrong way to work around a bug. Tested on a single device. Only supports a single Wave Plus. Does not construct a unique id for the sensor. Figured I may as well upload in case it's useful to someone else.*

If you have trouble with installation and configuration, visit the [Airthings Wave Home Assistant community discussion](https://community.home-assistant.io/t/air-quality-monitor-radon-meter-airthings-wave-plus/102836).

**Additional features and bug fixes are the responsibility of the community to implement (unless trivial to add).**
## Installation

### Step 1: Install Custom Components

Make sure [Home Assistant Community Store (HACS)](https://github.com/custom-components/hacs) is installed, then add the "Integration" repository: *gkreitz/hass-airthings-wave*.

Note:

* The 'master' branch of this custom component is considered unstable, alpha quality and not guaranteed to work.
* 
* Manual installation by direct download and copying is not supported, if you have issues, please first try installing this integration with HACS.

### Step 2: Configure

1. Find the MAC address for your Airthings Wave. See https://airthings.com/us/raspberry-pi/ for details.
2. Add the following to your `configuration.yaml` (or modify your `sensor` heading, if you already have one):

```yaml
sensor:
  - platform: airthings_wave
    model: waveplus
    mac: 00:11:22:AA:BB:CC # replace with MAC of your Airthings Wave+
```

```yaml
sensor:
  - platform: airthings_wave
    model: wave # or waveplus
    mac: 00:11:22:AA:BB:CC # replace with MAC of your Airthings Wave+
    unit_system: imperial # or metric
```

Then restart Home Assistant and if everything works, you'll have some new sensors named `sensor.airthings_{co2,humidity,longterm_radon,pressure,shortterm_radon,temperature,voc}`

### Known issues

* The unit_system imperial (Fahrenheit) is likely not working.
* Addition of elevation in meters config option to correct the pressure sensor to sea level conditions.

### See Also

* [Airthings Wave Plus discussion forum on Home Assistant](https://community.home-assistant.io/t/air-quality-monitor-radon-meter-airthings-wave-plus/102836)
* [Airthings for Home Assistant](https://github.com/custom-components/sensor.airthings_wave) (does not support Wave Plus)

