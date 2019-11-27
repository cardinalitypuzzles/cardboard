import os
import slack

from slack.errors import SlackApiError


class SlackClient:
    '''
    This is a wrapper class around the existing slack web client that allows for
    sending messages, creating channels, and joining channels.

    This is a singleton class.
    '''
    __instance = None

    @staticmethod
    def getInstance():
        ''' Static access method. '''
        if SlackClient.__instance == None:
            SlackClient()
        return SlackClient.__instance


    def __init__(self, announcement_channel_name="announcements"):
        ''' Private constructor. '''
        if SlackClient.__instance != None:
            raise Exception("SlackClient is a singleton and should not be "
                            "constructed multiple times. Use "
                            "SlackClient.getInstance() to access it.")

        else:
            self._slack_token = os.environ.get("SLACK_API_TOKEN", None)
            self._web_client = slack.WebClient(token=self._slack_token)
            self.announcement_channel_name = announcement_channel_name
            SlackClient.__instance = self


    def send_message(self, channel_name, message):
        '''
        Sends message to channel_name.
        '''
        self._web_client.chat_postMessage(channel=channel_name, text=message)


    def create_channel(self, puzzle_name):
        '''
        Returns the assigned channel id if able to create a channel.
        Otherwise, raises an exception.
        '''
        try:
            # By setting validate=False, the client will automatically clean up
            # special characters and make it fit under 80 characters.
            response = self._web_client.channels_create(name=puzzle_name,
                                                   validate=False)
            if response["ok"]:
                assigned_channel_name = response["channel"]["name"]
                channel_id = response["channel"]["id"]
                print(response)
                self.send_message(self.announcement_channel_name, "Channel " +
                                  assigned_channel_name +
                                  " created for puzzle titled " + puzzle_name
                                  + "!")
                return channel_id
        except SlackApiError as e:
            if (e.response['error'] == 'name_taken'):
                raise NameError('Slack channel name already exists.')
            raise e


    def join_channel(self, channel_name):
        '''
        Joins channel with given name. Assumes channel_name is valid and
        exists.
        '''
        self._web_client.channels_join(channel=channel_name)
