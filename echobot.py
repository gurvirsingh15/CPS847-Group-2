import settings

import os, time, re, sys

from datetime import datetime as dt

from slackclient import SlackClient

sclient = SlackClient(os.environ["ECHOBOT_API_KEY"])
echobot_id = 'U93SC5RA5'


MENTION_REGEX = "<@{}>(.*)".format(echobot_id)


def extract_message(message):
    matches = re.search(MENTION_REGEX, message)

    if (not (matches == None)):
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
    t = str(dt.now())[:19]
       
    log = """
 Time     {}
 Message  {}
 Channel  {}
 User     {}
    
    """.format(t, message, channel, user)
    
    sys.stderr.write(log)
    
    
    sclient.api_call(
        "chat.postMessage",
        channel=channel,
        text=message,
        user=user
    )


if __name__ == "__main__":
    
    if sclient.rtm_connect(with_team_state=False):
        sys.stderr.write('Echobot up n runnin\n')
        while True:
            message, channel, user = parse_command(sclient.rtm_read())

            if not message == None:
                echo_message(message,channel,user)

                time.sleep(1)
    else:
        print ("Connection failed")
