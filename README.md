PyLights
========

Ad-hoc script for turning on / off home lights using the PyWemo toolkit.

This is intended to replace the service offered by Belkin to perform these operations once it is sunset in January 2026.

# Installation
For your selected Python environment:

    pip3 install -r requirements.txt

# Execution
There are a few ways to run this script. These are configurable based on the 
`device_on` and `device_off` specified.

| device_on / device_off | Description                                                            |
|------------------------|------------------------------------------------------------------------|
| omit                   | Do not execute this condition.                                         |
| now                    | Execute right now.                                                     |
| sunrise                | Execute at sunrise; script sleeps until condition is met.              |
| sunset                 | Execute at sunset; script sleeps until condition is met.               |
| HH:MM                  | Exact hour / minute to turn off. Must be the same day it is turned on. |
| SS                     | Number of seconds to wait before toggling.                             |

If a sunset condition is requested, the `latitude` and `longitude` values must be specified.
These are decimal degrees for your geographic location.

## On/Off Method
Use the script to turn on or off at execution. This could be used on a cron
configuration to toggle a switch on/off at fixed times of day.

    schedule_lights.py --device_on now --device_name "My Light Name"

Turning off is the reverse request:

    schedule_lights.py --device_off now --device_name "My Light Name"

## Sunrise/Sunset Method
For sun events you may include your geolocation (latitude / longitude) and this is
used to determine when sun events occurs in your area. Once running in this mode, 
the script waits for either sunrise or sunset (assuming it is in the future). 

After sun events trigger the light on event, the method to keep the light on is 
determined from `device_off`.

For example, to turn on at sunset and off at 11:30 PM local time:

    schedule_lights.py --device_on sunset --device_off 21:30 --device_name "My Light Name"