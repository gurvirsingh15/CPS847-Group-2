import os
import time
import re
from slackclient import SlackClient

sclient = SlackClient(os.environ["SLACK_API_TOKEN"])
starterbot_id = None
MENTION_REGEX = "<.*>(.*)"


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
	sclient.api_call(
		"chat.postMessage",
		channel=channel,
		text=message,
		user=user
	)

if sclient.rtm_connect(with_team_state=False):
	print ("Running")
	while True:
		message, channel, user = parse_command(sclient.rtm_read())
		
		if not message == None:
			echo_message(message,channel,user)

		time.sleep(1)
else:
	print ("Connection failed")
