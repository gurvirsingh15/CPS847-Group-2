# loads .env contents
import settings

# use for approximate string matching
import difflib

import pandas as pd 

import os, time, sys
import re, json

from urllib.request import urlopen
from datetime import datetime as dt

from slackclient import SlackClient

keys = {
    'weatherbot': os.environ['WEATHERBOT_API_KEY'],
    'openweather': os.environ['OPENWEATHER_API_KEY']
}

client = SlackClient(keys['weatherbot'])
weatherbot_id = 'U93NEAZ24'

mention_regex = "<@{}>(.*)".format(weatherbot_id)

base_url = 'https://api.openweathermap.org/data/2.5/weather'

# from the world cities database : https://simplemaps.com/data/world-cities
cities = pd.read_csv('cities.csv').city

# emojis assigned to each description for great fun
emojis = {
    'broken clouds': 'sun_behind_cloud', 
    'clear sky': 'sun_with_face',
     'few clouds': 'sun_small_cloud', 
     'haze': 'fog', 
     'mist': 'fog', 
     'light rain': 'partly_sunny_rain', 
     'light snow': 'snowflake', 
     'moderate rain': 'umbrella_with_rain_drops', 
     'overcast clouds': 'cloud', 
     'scattered clouds': 'sun_small_cloud'
} 



def get_weather(city):
    """Gets the weather data for a given city"""

    # build the url string
    url = '{}?APPID={}&q={}'.format(base_url,
                                    keys['openweather'],
                                    city.replace(' ', '+'))
    # http get it
    try:
        res = urlopen(url)
    except:
        return {'error': 'url not found'}
    
    
    if res.code != 200:
        return {'error': 'invalid request'}
    
    try:
        data = json.loads(res.read().decode('utf8'))
    except:
        return {'error': 'malformed data'}

    return data

def extract_message(message):
    """Extracts message content from a mention"""
    
    matches = re.search(mention_regex, message)
    if not (matches == None):
        return matches.group(1)

def parse_command(information_recieved):
    """Parses information from RTM and extracts command and parameters"""
    for item in information_recieved:
        if item['type'] == "message" and not "subtype" in item:
            message = extract_message(item['text'])
            user = item['user']
            channel = item['channel']

            return message, channel, user

    return None,None,None

def handle_message(message, channel, user):
    """Main method to handle weather data queries"""

    
    # get the current time
    t = str(dt.now())[:19]

    # display message details
    log = """
 Time     {}
 Message  {}
 Channel  {}
 User     {}
    
    """.format(t, message, channel, user)
    
    sys.stderr.write(log)
    
    
    # check the world cities dataset for cities 
    # whose names are approximately the given text
    # 
    # example: new yrk --> New York
    matches = difflib.get_close_matches(message, cities)
   
    # if a city is found, grab the data for the first match
    # from the openweather API
    if len(matches):
            city = matches[0]
           
            data = get_weather(city)
            
            if not 'error' in data:
                # parse main fields
                desc = data['weather'][0]['description']
                
                temp = int(data['main']['temp']) - 273   # kelvin to celsius
                hum = data['main']['humidity']
                vis = data['visibility']

                # add an emoji if we've got one
                emoji = '' if not desc in emojis else ':{}:'.format(emojis[desc])

                # format the response
                
                header = '\n*{} Weather Report *'.format(city)
                sig = '\nCheers, \n\t *Weatherbot*'

                response = '\n\t'.join([
                        header,
                        'Description:       {}  {}'.format(desc, emoji),
                        'Temperature:       {}'.format(temp),
                        'Humidity:            {}'.format(hum),
                        'Visibility:            {}'.format(vis),
                        sig
                    ])
                
            else:
                response = ':sob: I couldn\'t get any weather data for "{}"'.format(message)
    else:
        response = ':sob: I couldn\'t find any cities matching "{}"'.format(message)


    # send the response
    client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response,
        user=user
    )


if __name__ == "__main__":
    if client.rtm_connect(with_team_state=False):
        print('Weatherbot ready 2 rumbl')
        while True:
            message, channel, user = parse_command(client.rtm_read())

            if not message == None:
                handle_message(message,channel,user)
            
        time.sleep(1)
    else:
        print ("Connection failed")
