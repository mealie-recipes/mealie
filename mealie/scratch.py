import collections

import pdfkit
import requests

from db.mongo_setup import global_init

Cron = collections.namedtuple("Cron", "hours minutes")


# def cron_parser(time_str: str) -> Cron:
#     time = time_str.split(":")
#     cron = Cron(hours=time[0], minutes=time[1])

#     print(cron.hours, cron.minutes)


# cron_parser("12:45")

URL = "https://home.homelabhome.com/api/webhook/test_msg"
from services.meal_services import MealPlan

global_init()
todays_meal = MealPlan.today()

requests.post(URL, todays_meal)
