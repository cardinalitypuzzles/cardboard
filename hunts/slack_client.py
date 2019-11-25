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
        Returns the assigned channel name if able to create a channel.
        Otherwise, raises an exception.
        '''
        try:
            # By setting validate=False, the client will automatically clean up
            # special characters and make it fit under 80 characters.
            response = self.client.channels_create(name=puzzle_name,
                                                   validate=False)
            if response["ok"]:
                assigned_channel_name = response["channel"]["name"]
                self.send_message(self.root_channel_name, "Channel " +
                                  assigned_channel_name +
                                  " created for puzzle titled " + puzzle_name
                                  + "!")
                return assigned_channel_name
        except SlackApiError as e:
            if (e.response['error'] == 'name_taken'):
                raise NameError('Slack channel name already exists.')
            raise e
