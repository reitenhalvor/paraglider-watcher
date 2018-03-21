# -*- coding: utf-8 -*-

from collections import defaultdict, OrderedDict
from datetime import datetime
from pgSite import ParagliderSite
import pandas as pd
import numpy as np

class WeatherAnalyser:

    def __doesDataMeetConstraints(self, data, constraints, too_late=19, too_early=7):
        # takes a row of a df as input
        lims = constraints # just rename to make shorter

        # check wind speed
        if data['wind_speed'] > max(lims['wind_speed']) or data['wind_speed'] < min(lims['wind_speed']):
            return False

        # check wind direction
        dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
        subs = dirs.index(lims['wind_dir'][0])

        j = dirs.index(lims['wind_dir'][0])
        k = dirs.index(lims['wind_dir'][1])

        subs = dirs[j:] + dirs[:(k+1)] if j > k else dirs[j:(k+1)]
        if data['wind_dir_txt'] not in subs:
            return False

        # check for any precipitation
        if data['precipitation'] > 0:
            return False

        # check if time is too late
        times = [data['time_from'].hour, data['time_to'].hour]

        if times[0] >= too_late or times[0] == 0 or times[1] <= too_early:
            return False

        return True

    def getTimeIntervals(self, times, interval_size = 6, min_elements = 2):
        # min_elements ~ the minimum number of "objects" in a interval
        # interval_size ~ the difference between one element and the next
        times = sorted(times) # sort the input list of datetime objects

        intervals = []
        curr_interval = []

        for i in range (1,len(times)):
            diff_down = times[i] - times[i-1]

            if diff_down.seconds/3600.0 == interval_size:
                if len(curr_interval)==0: curr_interval.append(times[i-1])
                curr_interval.append(times[i])
            else:
                if len(curr_interval) >= min_elements:
                    intervals.append((min(curr_interval),max(curr_interval)))
        if len(curr_interval) >= min_elements:
            intervals.append((min(curr_interval), max(curr_interval)))

        return intervals

    def getAverageWeatherValues(self, df, from_time, to_time):
        avg_values = {'time_from': from_time, 'time_to': to_time, 'temp': 0, 'precipitation': 0,
                        'wind_dir': 0, 'wind_dir_txt': '', 'wind_speed': 0}

        if (from_time > to_time):
            raise Exception("Invalid input...")

        filtered_df = df[df.time_from >= from_time]
        filtered_df = filtered_df[filtered_df.time_to <= to_time]

        if not filtered_df.empty:
            length = len(filtered_df)

            for attr in avg_values.keys():
                if filtered_df.dtypes[attr] in ('int64','float64'):
                    avg_values[attr] = round(sum(filtered_df[attr])/length,2)
                else:
                    continue

        # lastly calculate the compass direction
        avg_values['wind_dir_txt'] = self.degreesToCompass(avg_values['wind_dir'])
        return avg_values

    def degreesToCompass(self,deg):
        directions = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
        deg = int(deg/(360/len(directions)) + .5)
        return directions[(deg % len(directions))]

    def compassToDegrees(self,direction):
        directions = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
        degrees = np.linspace(0,360,len(directions)+1) - 360/(2*len(directions))
        degrees[degrees < 0] += 360
        bounds = zip(degrees[:-1], degrees[1:])
        compass_bounds = dict(zip(directions,bounds))
        return compass_bounds[direction]

    def getRecommendations(self, df, pgSite):
        recommendations = {'df': None, 'intervals': {}, 'text': ''}
        recommended_df = pd.DataFrame(columns = df.columns)
        intervals_df = pd.DataFrame(columns = df.columns)
        intervals_txt = []

        for row in range(len(df)):
            datarow = df.loc[row+1]
            if (self.__doesDataMeetConstraints(datarow, pgSite.constraints)):
                # then add to recommended_df
                recommended_df.loc[len(recommended_df)+1] = datarow

        # get time intervals per day
        rec_days = recommended_df["time_from"].map(lambda t: t.date()).unique()
        for day in rec_days:
            day_mask = recommended_df['time_from'].map(lambda t: t.date()) == day
            data = recommended_df[day_mask]
            times = set(data['time_from'].append(data['time_to']))

            intervals = self.getTimeIntervals(times, pgSite.hour_interval)
            for interval in intervals:
                avg_vals = self.getAverageWeatherValues(data, interval[0], interval[1])
                intervals_df.loc[len(intervals_df)+1] = [avg_vals['time_from'],
                                                         avg_vals['time_to'],
                                                         avg_vals['temp'],
                                                         avg_vals['precipitation'],
                                                         avg_vals['wind_dir'],
                                                         avg_vals['wind_dir_txt'],
                                                         avg_vals['wind_speed']]

                intervals_txt.append(self.__dataToString__(intervals_df.loc[len(intervals_df)], pgSite))

        recommendations['text'] = intervals_txt
        recommendations['df'] = recommended_df
        recommendations['intervals'] = intervals_df
        return recommendations

    def __dataToString__(self, data, pgSite):
        string = ("PG Alarm @ site \"{}\" ({}: {} - {})\n" +
                  "WindSpeed: {} m/s, WindDirection: {} {}, Temp: {}C\n" +
                  "Constraints for site: {} degrees\n" +
                  "::: ::: ::: ::: ::: ::: ::: ::: ::: "
                 ).format(
                    pgSite.location,
                    data['time_from'].date(), data['time_from'].time(),
                    data['time_to'].time(), data['wind_speed'], data['wind_dir'],
                    data['wind_dir_txt'], data['temp'],
                    pgSite.constraints['wind_dir']
                 )

        return string
