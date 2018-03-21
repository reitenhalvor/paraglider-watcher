# -*- coding: utf-8 -*-

import urllib2
import xmltodict
import pandas as pd
from datetime import datetime, timedelta

class WeatherScraper:
    pd.set_option('display.width', 130)

    def __init__(self, location, url):
        self.location = location
        self.url = url
        self.data = None

    def __updateWeatherData(self):
        try:
            file = urllib2.urlopen(self.url)
            raw_data = file.read()
            raw_data = xmltodict.parse(raw_data)
            file.close()

            self.data = raw_data["weatherdata"]["forecast"]["tabular"]["time"]

        except:
            print "There was an error scraping www.yr.no for " + self.location
            self.data = None

    def getWeatherData(self, number_of_days=None):
        self.__updateWeatherData()
        if self.data == None:
            return None

        weather_df = pd.DataFrame(columns = ['time_from','time_to','temp','precipitation',
                                             'wind_dir','wind_dir_txt','wind_speed'
                                             ])
        included_days = set([])
        hour_interval = 1 if self.url.endswith("time_for_time.xml") else 6

        for elem in self.data:
            day = elem["@from"].split("T")[0]
            hour = elem["@from"].split("T")[1]
            time_from = datetime.strptime(day+" "+hour, "%Y-%m-%d %H:%M:%S")
            time_to = time_from + timedelta(hours=hour_interval)
            temp = float(elem["temperature"]["@value"])
            precipitation = float(elem["precipitation"]['@value'])
            wind_dir = float(elem["windDirection"]['@deg'])
            wind_dir_txt = str(elem["windDirection"]['@code'])
            wind_speed = float(elem["windSpeed"]['@mps'])

            if day not in included_days:
                included_days.add(day)
                if isinstance(number_of_days,int) and len(included_days) > number_of_days:
                    break

            if time_from not in weather_df.time_from:
                weather_df.loc[len(weather_df) + 1] = [time_from,time_to,temp,precipitation,wind_dir,wind_dir_txt,wind_speed]

        weather_df.iloc[0,1] = weather_df.iloc[1,0] # correct time mistake
        return weather_df
