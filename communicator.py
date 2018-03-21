import requests, json
slack_url = 'https://hooks.slack.com/services/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'

def sendSlackMessage(text):
    try:
        slack_payload = {   "text" : text,
                            "username": "paraglider-bot",
                            "icon_emoji": ":money_with_wings:"
                        }
        response = requests.post(slack_url, data=json.dumps(slack_payload), headers={"Content-Type":"application/json"})

        if response.status_code != 200:
            raise ValueError("Request to slack returned an error %s the response is: \n%s" %(response.status_code, response.text))

    except:
        print("Error in Communicator: Could not send message")
