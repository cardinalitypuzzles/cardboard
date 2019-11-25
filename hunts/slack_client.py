import os
import slack

class SlackClient:
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = slack.WebClient(token=slack_token)
    root_channel_name = "small-board"

    def send_message(self, channel_name, message):
        self.client.chat_postMessage(channel=channel_name, text=message)

    def create_channel(self, puzzle_name):
        '''
        Returns boolean value. True if a new channel was successfully created. False otherwise.
        '''
        # By setting validate=False, the client will automatically clean up
        # special characters and make it fit under 80 characters.
        response = self.client.channels_create(name=puzzle_name, validate=False)
        print(response)
        if response["ok"]:
           channel_name = response["channel"]["name"]
           self.send_message(self.root_channel_name, "Channel " + channel_name + " created for puzzle titled " + puzzle_name + "!")
           return True
        return False
        
       

