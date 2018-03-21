# -*- coding: utf-8 -*-

from weatherScraper import WeatherScraper

class ParagliderSite:

    def __init__(self, location, url, wind_dir_constr, wind_speed_constr):
        self.location = location
        self.constraints = {'wind_dir': wind_dir_constr,
                            'wind_speed': wind_speed_constr}
        self.url = url
        self.hour_interval = 1 if url.endswith("time_for_time.xml") else 6

    def getLocation():
        return self.location

    def getConstraints():
        return self.constraints

    def fetchData(self,number_of_days = 3):
        ws = WeatherScraper(self.location, self.url)
        return ws.getWeatherData(number_of_days)

    def __str__(self):
        text = ("::: {} ::: WindDir: {}, WindSpeed: {}\n"
                ).format(self.location, self.constraints['wind_dir'],self.constraints['wind_speed'])
        return text
