# CPS847-Group-2


## Weatherbot & Echobot


### Requirements

* Python3.x

* `pip3 install -r requirements.txt`


The weatherbot slackbot uses the [Open Weather Map API](https://openweathermap.org) to fetch data by city name. This requires an API key, which can then be stored under `.env` alongside
the slackbot api key:



```
# .env
SLACKBOT_API_KEY="the slackbot api key"
OPENWEATHER_API_KEY="the openweather api key"
```

Alternatively, you can export these before use:

```
$ export SLACKBOT_API_KEY="the slackbot api key"
$ export OPENWEATHER_API_KEY="the openweather api key"
```

Or save them as environment variables in your `.bashrc`


```
$ echo "SLACKBOT_API_KEY='the slackbot api key'" >> $HOME/.bashrc
$ echo "OPENWEATHER_API_KEY='the openweather api key'" >> $HOME/.bashrc
```


### Usage


Run the weatherbot: 

```
$ python3 weatherbot.py
```



In slack, grab the weather for any city with `@weatherbot <city>`. Weatherbot will use `difflib` to look for close matches of the input string with the list of all cities contained in `cities.csv`. If a close match is found, weatherbot grabs the city's weather data and pulls out the key features. 

To make things really sick, weatherbot even maps each high-level weather description to an emoji!!!!

See the example below where a real live slack user with spelling difficulties gets real live weather data from weatherbot!!!



![img](weatherbot.png)
