from django.db.models import Count
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from environs import Env
import re
import requests
from datetime import timedelta
from datetime import datetime

from .models import *

env = Env()
env.read_env()


def deg_to_dir(deg, *args, **kwargs):
    if round(deg) < 45 or 315 <= round(deg):
        dir = "East"
        return dir
    elif 45 <= round(deg) < 135:
        dir = "North"
        return dir
    elif 135 <= round(deg) < 225:
        dir = "West"
        return dir
    elif 225 <= round(deg) < 315:
        dir = "South"
        return dir


def identify_icon_code(icon_name, *args, **kwargs):
    if re.search("^01", icon_name):
        code = 2
    elif re.search("^02", icon_name):
        code = 3
    elif re.search("^03", icon_name):
        code = 5
    elif re.search("^04", icon_name):
        code = 6
    elif re.search("^09", icon_name):
        code = 10
    elif re.search("^10", icon_name):
        code = 4
    elif re.search("^11", icon_name):
        code = 11
    elif re.search("^13", icon_name):
        code = 14
    elif re.search("^50", icon_name):
        code = 8
    return f"icon-{code}.svg"


def check_location_exstiance(location, *args, **kwargs):
    api_key = env.str("wth_api_key")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    wth = requests.get(url).json()
    return wth


def geocode_forward_api_req(location):
    url = "https://forward-reverse-geocoding.p.rapidapi.com/v1/forward"
    querystring = {
        "format": "json",
        "city": location,
        "accept-language": "en",
        "polygon_threshold": "0.0",
    }
    headers = {
        'x-rapidapi-host': env("x-rapidapi-host"),
        'x-rapidapi-key': env("x-rapidapi-key"),
    }
    resp_api = requests.get(url, headers=headers, params=querystring).json()
    return resp_api


def wth_api_req(lon, lat, unit):
    print(unit)
    api_key = env.str("wth_api_key")
    url = (f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}"
           f"&exclude=alerts,minutely&units={unit}&appid={api_key}")
    resp_api = requests.get(url).json()
    return resp_api


def get_current_weather(resp_json, location):
    current = resp_json.get("current")
    context = {
        "temp": round(current.get("temp")),
        "humidity": current.get("humidity"),
        "wind_s": round(current.get("wind_speed")),
        "wind_dir": deg_to_dir(current.get("wind_deg")),
        "icon": identify_icon_code(current.get("weather")[0].get("icon")),
        "location": location.title(),
    }
    return context


def get_daily_weather(resp_json):
    daily = resp_json.get("daily")[1:]
    contexts = {f"day{i+1}": "" for i in range(len(daily))}
    i = 0
    for k, v in contexts.items():
        contexts[k] = {
            "max": round(daily[i].get("temp").get("max")),
            "min": round(daily[i].get("temp").get("min")),
            "icon": identify_icon_code(daily[i].get("weather")[0].get("icon")),
            "time_delta": timedelta(days=i+1),
        }
        i += 1
    contexts = {"daily": contexts}
    return contexts
    

def get_hourly_weather(resp_json):
    hourly = resp_json.get("hourly")
    contexts = {f"hour{i+1}": "" for i in range(len(hourly))}
    i = 0
    for k, v in contexts.items():
        contexts[k] = {
            "time": datetime.utcfromtimestamp(hourly[i].get("dt")),
            "temp": round(hourly[i].get("temp")),
            "icon": identify_icon_code(hourly[i].get("weather")[0].get("icon")),
            "wind_speed": round(hourly[i].get("wind_speed")),
            "wind_dir": deg_to_dir(hourly[i].get("wind_deg")),
        }
        i += 1
    contexts = {"hourly": contexts}
    return contexts


def set_default_city(request, city, *args, **kwargs):
    city_field = City.objects.get(city=city)
    user_pwth = PersonalWeather.objects.get(user=request.user)
    default = Default.objects.filter(
        personalweather=user_pwth)
    default.update(default=city_field)


def set_unit(request, unit):
    try:
        user_wth = PersonalWeather.objects.get(user=request.user)
        if user_wth.unit != unit:
            user_wth.unit = unit
            user_wth.save()
    except ObjectDoesNotExist:
        user_wth = PersonalWeather.objects.create(user=request.user)
        user_wth.unit = unit
        user_wth.save()


def send_contact_email(name, message):
    url = "https://email-sender1.p.rapidapi.com/"
    querystring = {"txt_msg": f"{message}", "to": "samanzand84@gmail.com", "from": "Weatherapp", "subject": f"Contact from {name}",
                   "bcc": "bcc-mail@gmail.com", "reply_to": "djsolutions.client@gmail.com", "html_msg": f"<html><body><b>User: {name}</b><br><p>{message}</p></body></html>", "cc": "djsolutions.client@gmail.com"}
    payload = "{\n    \"key1\": \"value\",\n    \"key2\": \"value\"\n}"
    headers = {
        'content-type': "application/json",
        'x-rapidapi-host': "email-sender1.p.rapidapi.com",
        'x-rapidapi-key': "161b65c3ffmshc4912656486e5a6p18911cjsn34a09bcbe87e"
    }
    requests.post(url, data=payload, headers=headers,
                  params=querystring)
