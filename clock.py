import datetime
import pytz
import os
from typing import Optional
from singleton import Singleton


class ClockService(metaclass=Singleton):
    def __init__(self, timezone: Optional[str] = None):
        if timezone:
            self.timezone = timezone
        elif os.environ.get("TZ"):
            self.timezone = os.environ.get("TZ")
        else:
            raise NameError("either a timezone or TZ enviroment variable must be provided")

    def now(self, strftime: Optional[str] = None):
        datetime_object = datetime.datetime.now().astimezone(pytz.timezone(self.timezone))
        if strftime:
            return datetime_object.strftime(strftime)
        return datetime_object

    def greeting(
        self,
        night_to_day: Optional[int] = 6,
        day_to_afternoon: Optional[int] = 12,
        afternoon_to_night: Optional[int] = 18,
    ):
        now = self.now()
        if int(now.strftime("%H")) > night_to_day and int(now.strftime("%H")) < day_to_afternoon:
            return f"Bom dia"
        elif int(now.strftime("%H")) >= day_to_afternoon and int(now.strftime("%H")) < afternoon_to_night:
            return f"Boa tarde"
        else:
            return f"Boa noite"
