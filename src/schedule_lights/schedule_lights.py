"""
Schedule activation for a Belkin Wemo lightswitch. Use the `device_on` and `device_off`
parameters to control when to turn on/off the specified switch.
"""
import argparse
import pywemo
import pytz
import re

from datetime import datetime
from datetime import timedelta
from datetime import time
from time import sleep
from timezonefinder import timezonefinder

from astral.location import LocationInfo
from astral.sun import sun


class ToggleSwitch:
    OFF = 0,
    ON = 1

# patterns to match for on/off time based expression
MATCH_SECONDS = "^\d+$"
MATCH_HOUR_MINUTE = "^\d+:\d+$"

def device_mode_param(param, pat=re.compile(r"^(omit|now|sunrise|sunset|\d+|\d+:\d+)$")):
    if not pat.match(param):
        raise argparse.ArgumentTypeError("Unsupported device toggle [ omit | now | sunrise | sunset | HH:MM | SS ]")
    return param

def compute_seconds_to_sunrise(latitude, longitude, tznow):
    """
    Calculate the seconds to sunrise time for a latitude and longitude.

    Args:
        latitude (float):  Latitude value.
        longitude (float):  Longitude value.
        tznow (datetime, Optional): the current date+time

    Returns:
        Number of seconds to sunset for the current day. If sunset has already occurred then return zero (0).
    """
    tf = timezonefinder.TimezoneFinder()
    timezone = tf.certain_timezone_at(lat=latitude, lng=longitude)

    # identify timezone and modify if necessary
    # use the parameter specific time for testing purposes
    tz = pytz.timezone(timezone)
    now_tz = tznow if tznow else datetime.now(tz)

    # Get all sun events for the date and location
    location = LocationInfo("", "", timezone, latitude=latitude, longitude=longitude)
    sun_data = sun(location.observer, date=now_tz.date(), tzinfo=tz)

    # extract the sunset time datetime
    sunrise_datetime = sun_data["sunrise"]

    # delta of time from now to sunset
    sunrise_from_now = (sunrise_datetime - now_tz).total_seconds()

    # return seconds to wait for sunset unless it has already passed
    return int(sunrise_from_now) if sunrise_datetime > now_tz else 0

def compute_seconds_to_sunset(latitude, longitude, tznow=None):
    """
    Calculate the seconds to sunset time for a latitude and longitude.

    Args:
        latitude (float):  Latitude value.
        longitude (float):  Longitude value.
        tznow (datetime, Optional): the current date+time

    Returns:
        Number of seconds to sunset for the current day. If sunset has already occurred then return zero (0).
    """
    tf = timezonefinder.TimezoneFinder()
    timezone = tf.certain_timezone_at(lat=latitude, lng=longitude)

    # identify timezone and modify if necessary
    # use the parameter specific time for testing purposes
    tz = pytz.timezone(timezone)
    now_tz = tznow if tznow else datetime.now(tz)

    # Get all sun events for the date and location
    location = LocationInfo("", "", timezone, latitude=latitude, longitude=longitude)
    sun_data = sun(location.observer, date=now_tz.date(), tzinfo=tz)

    # extract the sunset time datetime
    sunset_datetime = sun_data["sunset"]

    # delta of time from now to sunset
    sunset_from_now = (sunset_datetime - now_tz).total_seconds()

    # return seconds to wait for sunset unless it has already passed
    return int(sunset_from_now) if sunset_datetime > now_tz else 0


def device_sleep(condition, latitude, longitude):
    """
    Sleep until the condition of day has been reached.

    Args:
        condition (str): condition for sleep which is one of omit, now, sunset, HH:MM, [seconds]
        latitude (float, Optional): Latitude of device
        longitude (float, Optional: Longitude of device

    Return:
        None
    """

    # default is negative value that will not sleep
    # this covers condition omit and now
    seconds_to_sleep = -1

    # if sunrise then compute time until sunrise
    if "sunrise" == condition:
        if not latitude:
            raise ValueError(f"Latitude of device is required")

        if not longitude:
            raise ValueError(f"Longitude of device is required")

        seconds_to_sleep = compute_seconds_to_sunrise(latitude, longitude)


    # if sunset then compute time until sunset
    if "sunset" == condition:
        if not latitude:
            raise ValueError(f"Latitude of device is required")

        if not longitude:
            raise ValueError(f"Longitude of device is required")

        seconds_to_sleep = compute_seconds_to_sunset(latitude, longitude)

    # specific time is n seconds
    if re.search(MATCH_SECONDS, condition):
        seconds_to_sleep = int(condition)

    # specific time is hh:mm
    if re.search(MATCH_HOUR_MINUTE, condition):
        tonight = datetime.now() + timedelta(days=1)
        midnight = datetime.combine(tonight.date(), time())

        # seconds_remaining_to_midnight = 86400 - off_at_seconds
        time_of_day = datetime.strptime(condition, "%H:%M").time()
        shutoff = datetime.combine(midnight.date(), time_of_day)
        seconds_to_sleep = (shutoff - tonight).total_seconds()

    # if there is a positive number of seconds to sleep then wait
    if seconds_to_sleep > 0:
        print(f"sleeping seconds_to_sleep={seconds_to_sleep} minutes_to_sleep={int(seconds_to_sleep/60)}\n")
        sleep(seconds_to_sleep)


#
def find_device(device_name):
    """
    Locate device by name or return null.

    Args:
        device_name (str): Name of the device to find

    Return:
         Device or None if not found
    """
    devices = pywemo.discover_devices()

    for device in devices:
        print(f"Found device {device}")
        if (device.name == device_name):
            return device

    return None

def device_toggle(toggle, device, condition, latitude, longitude):
    """
     Toggle device either ON or OFF based on the condition specified.

     Args:
        toggle (int): Method to invoke on the switch either ON or OFF
        device (pywemo.Device): Device to toggle:
        condition (str): Condition to execute which is one of omit, now, sunset, HH:SS or seconds.
        latitude (float, optional): Latitude of the device; needed for sunset condition.
        longitude (float, optional): Longitude of the device; needed for sunset condition.
    """
    # if omit then immediately return
    if "omit" == condition:
        return

    # execute sleep / delay before on/off
    device_sleep(condition, latitude, longitude)

    if toggle == ToggleSwitch.ON:
        device.on()
    else:
        device.off()


def main():

    # parse arguments from command line
    parser = argparse.ArgumentParser(prog="ScheduleLights", description="Toggle lights on / off at sunset")
    parser.add_argument("--device_name", help="Name of the device to toggle.", type=str, required=True)
    parser.add_argument("--latitude", help="Latitude of your location.", type=float, required=False)
    parser.add_argument("--longitude", help="Longitude of your location.", type=float, required=False)
    parser.add_argument("--device_on", help="Turn on at this condition; default is to not execute any on mode.", type=device_mode_param, default="omit")
    parser.add_argument("--device_off", help="Turn off at this condition; default is to not execute any off mode.", type=device_mode_param, default="omit")

    args = parser.parse_args()

    # identify the device or exit
    device = find_device(args.device_name)

    if not device:
        print("Device not found")
        exit(1)

    device_toggle(ToggleSwitch.ON, device, args.device_on, args.latitude, args.longitude)
    device_toggle(ToggleSwitch.OFF, device, args.device_off, args.latitude, args.longitude)

if __name__ == "__main__":
    main()