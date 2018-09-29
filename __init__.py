"""Weather Extension, gets information from openweatherapi"""

from albertv0 import *

import urllib3
import json
from datetime import datetime, timedelta, timezone
import time

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Forecast"
__version__ = "0.1"
__trigger__ = "forecast "
__author__ = "Bharat Kalluri"
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


def handleQuery(query):
    if query.isTriggered:
        if query.string.strip():
            return showForecast(query)
        else:
            return Item(
                id=__prettyname__,
                icon=iconLookup("weather-overcast"),
                text=__prettyname__,
                subtext="Type in the city name",
                completion=query.rawString,
            )


def showForecast(query):
    qurl = (
        "http://api.openweathermap.org/data/2.5/forecast?appid=62dbe63b5ed5c90264b4d3c0054bd993&type=accurate&units=metric&q="
        + query.string.strip()
    )

    try:
        res = http.request("GET", qurl)
        data = json.loads(res.data)
    except:
        critical("No Internet!")
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
        itemArr = []

        # Initial Item showing info
        tempItem = Item(
            id=__prettyname__,
            icon=iconLookup("dialog-information"),
            text="Weather in {}".format(data["city"]["name"]),
        )
        itemArr.append(tempItem)

        # Get all the required timestamps
        requiredTs = []
        for i in range(1, 6):
            tempDate = int(
                (
                    datetime(now.year, now.month, now.day, 12, tzinfo=timezone.utc)
                    + timedelta(days=i)
                ).timestamp()
            )
            requiredTs.append(tempDate)

        tempItem = makeItem(data["list"][0])
        itemArr.append(tempItem)

        for obj in data["list"]:
            if obj["dt"] in requiredTs:
                tempItem = makeItem(obj)
                itemArr.append(tempItem)

        return itemArr


def makeItem(jsonObj):
    dateEpoch = jsonObj["dt"]
    return Item(
        id=__prettyname__,
        icon=iconLookup(
            weatherDict.get(jsonObj["weather"][0]["description"], "weather-overcast")
        ),
        text="{}: {}".format(
            time.strftime("%d %B", time.localtime(dateEpoch)),
            jsonObj["weather"][0]["main"],
        ),
        subtext="High: {:.1f}°C ({:.1f}°F) Low: {:.1f}°C ({:.1f}°F) Humidity: {}%".format(
            jsonObj["main"]["temp_min"],
            fahrenheitConverter(jsonObj["main"]["temp_min"]),
            jsonObj["main"]["temp_max"],
            fahrenheitConverter(jsonObj["main"]["temp_max"]),
            jsonObj["main"]["humidity"],
        ),
    )


def fahrenheitConverter(celsius):
    return 9 / 5 * celsius + 32
