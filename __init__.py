"""Weather Extension, gets information from openweather API"""

from albert import *

import urllib3
import json
from datetime import datetime, timedelta, timezone
import time

__iid__ = "PythonInterface/v0.4"
__title__ = "Forecast"
__prettyname__ = "Forecast"
__version__ = "0.0.2"
__triggers__ = "fc "
__authors__ = "Bharat Kalluri"
__dependencies__ = []

http = urllib3.PoolManager()

weatherDict = {
    "clear sky": "weather-clear",
    "few clouds": "weather-few-clouds",
    "scattared clouds": "weather-overcast",
    "broken clouds": "weather-overcast",
    "shower rain": "weather-showers",
    "rain": "weather-showers",
    "thunderstorm": "weather-storm",
    "snow": "weather-snow",
    "mist": "weather-fog",
}

API_URL = "http://api.openweathermap.org/data/2.5/forecast?appid=" \
          "62dbe63b5ed5c90264b4d3c0054bd993&type=accurate&units=metric&q="


def handleQuery(query):
    if query.isTriggered:
        # Prevent rate limiting
        time.sleep(0.5)
        if not query.isValid:
            return

        if query.string.strip():
            return show_forecast(query)
        else:
            return Item(
                id=__prettyname__,
                icon=iconLookup("weather-overcast"),
                text=__prettyname__,
                subtext="Type in the city name",
                completion=query.rawString,
            )


def show_forecast(query):
    qurl = API_URL + query.string.strip()

    try:
        res = http.request("GET", qurl)
        data = json.loads(res.data)
    except:
        return [
            Item(
                id=__prettyname__,
                icon=iconLookup("dialog-warning"),
                text="Is internet working?",
                subtext="We could not query, check your internet connection",
                completion=query.rawString,
            )
        ]
    if data["cod"] == "404":
        return [
            Item(
                id=__prettyname__,
                icon=iconLookup("weather-overcast"),
                text=__prettyname__,
                subtext="The city name does not exist in the database",
                completion=query.rawString,
            )
        ]
    else:
        now = datetime.utcnow()
        item_arr = [Item(
            id=__prettyname__,
            icon=iconLookup("dialog-information"),
            text="Weather in {}".format(data["city"]["name"]),
        )]
        # Initial Item showing info

        # Get all the required timestamps
        required_ts = []
        for i in range(1, 6):
            temp_date = int(
                (
                    datetime(now.year, now.month, now.day, 12, tzinfo=timezone.utc)
                    + timedelta(days=i)
                ).timestamp()
            )
            required_ts.append(temp_date)

        temp_item = make_item(data["list"][0])
        item_arr.append(temp_item)

        for obj in data["list"]:
            if obj["dt"] in required_ts:
                temp_item = make_item(obj)
                item_arr.append(temp_item)

        return item_arr


def make_item(json_obj):
    date_epoch = json_obj["dt"]
    return Item(
        id=__prettyname__,
        icon=iconLookup(
            weatherDict.get(json_obj["weather"][0]["description"], "weather-overcast")
        ),
        text="{}: {}".format(
            time.strftime("%d %B", time.localtime(date_epoch)),
            json_obj["weather"][0]["main"],
        ),
        subtext="High: {:.1f}°C ({:.1f}°F) Low: {:.1f}°C ({:.1f}°F) Humidity: {}%".format(
            json_obj["main"]["temp_min"],
            fahrenheit_converter(json_obj["main"]["temp_min"]),
            json_obj["main"]["temp_max"],
            fahrenheit_converter(json_obj["main"]["temp_max"]),
            json_obj["main"]["humidity"],
        ),
    )


def fahrenheit_converter(celsius):
    return 9 / 5 * celsius + 32
