# -*- coding: utf-8 -*-

from pgSite import ParagliderSite
from weatherAnalyser import WeatherAnalyser
from communicator import sendSlackMessage
import pandas as pd
import time

url = 'https://www.yr.no/sted/'
end = 'varsel.xml'

pgSites = {
    'Lions Head' : ParagliderSite('Lions Head', url + "Sør-Afrika/Western_Cape/Cape_Town/" + end,
                                    wind_dir_constr = ['SW','W'], wind_speed_constr = [1,6]),
    'Hermanus' : ParagliderSite('Hermanus', url + "Sør-Afrika/Western_Cape/Cape_Town/" + end,
                                    wind_dir_constr = ['SE','S'], wind_speed_constr = [1,6]),
    'Grøtterud' : ParagliderSite('Grøtterud', url + "Norge/Buskerud/Kongsberg/Hvittingfoss/" + end,
                                    wind_dir_constr = ['SE','SW'], wind_speed_constr = [1,6]),
}

analyst = WeatherAnalyser()
recommendations = {}

#while True:
print "Fetching data..."
start_time = time.time()


rec_df = pd.DataFrame(columns = [   'site', 'time_from', 'time_to',
                                    'temp','precipitation', 'wind_dir',
                                    'wind_dir_txt','wind_speed'
                                ])
for location in pgSites.keys():
    site = pgSites[location]
    df = site.fetchData(number_of_days = 5)
    local_recommendation = analyst.getRecommendations(df, site)['intervals']

    if not local_recommendation.empty:
        local_recommendation.insert(0,'site',location)
        rec_df = rec_df.append(local_recommendation)

if not rec_df.empty:
    send_df = rec_df.drop(['precipitation'], axis = 1)
    message = ( "*New PG alert* (" + time.strftime("%Y-%m-%d %H:%M", time.gmtime()) + ")\n" +
                "```" + repr(send_df) + "```")

    sendSlackMessage(message)
    print rec_df.to_string
else:
    print "No recommendations :("

print "finalized in " + str(time.time() - start_time) + " seconds."

    #time.sleep(10) # sleep for three days
