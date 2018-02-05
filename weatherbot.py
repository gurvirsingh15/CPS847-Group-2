import settings
import os, time, sys
import re, difflib

from slackclient import SlackClient


client = SlackClient(os.environ["SLACKBOT_API_KEY"])
starterbot_id = None

MENTION_REGEX = "<.*>(.*)"

base_url = 'https://api.openweathermap.org/data/2.5/weather?APPID={}'.format(os.environ['OPENWEATHER_API_KEY'])

# from the world cities database : https://simplemaps.com/data/world-cities
# v. convenient
cities = pd.read_csv('cities.csv').city
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
	url = '{}&q={}'.format(base_url, city)
	res = urlopen(url)

	if res.code != 200:
		sys.stderr.write('error: {}'.format(res.code))
		return

	data = json.loads(res.read().decode('utf8'))

	return data


def extract_message(message):
	matches = re.search(MENTION_REGEX, message)
	return matches.group(1)

def parse_command(information_recieved):
	for item in information_recieved:
		if item['type'] == "message" and not "subtype" in item:
			message = extract_message(item['text'])
			user = item['user']
			channel = item['channel']
			return message, channel, user

	return None,None,None

def echo_message(message, channel, user):
	try:

		matches = difflib.get_close_matches(message, cities)

		if len(matches) == 0:
			response = 'Can\'t even find anything close to that!'
		else:
			city = matches[0]
			query = city.replace(' ', '+')
			data = get_weather(query)

			desc = data['weather'][0]['description']
			temp = int(data['main']['temp']) - 273
			hum = data['main']['humidity']
			vis = data['visibility']

			emoji = '' if not desc in emojis else ':{}:'.format(emojis[desc])

			print(desc)
			print(desc in emojis)

			header = '*{} Weather Report {}*'.format(city, emoji)

			sig = '\nCheers, \n\t *Weatherbot*'

			response = '\n\t'.join([
					header,
					'Description:       {}'.format(desc),
					'Temperature:       {}'.format(temp),
					'Humidity:          {}'.format(hum),
					'Visibility:        {}'.format(vis),
					sig
				])


		

		client.api_call(
			"chat.postMessage",
			channel=channel,
			text=response,
			user=user
		)

	except:
		pass

if __name__ == "__main__":
	if client.rtm_connect(with_team_state=False):
		print('sup')
		while True:
			message, channel, user = parse_command(client.rtm_read())
			
			if not message == None:
				echo_message(message,channel,user)

			time.sleep(1)
	else:
		print ("Connection failed")