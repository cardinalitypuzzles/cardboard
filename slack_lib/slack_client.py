import os
import slack

from django.conf import settings


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
            token = settings.SLACK_API_TOKEN
            if token:
                self._enabled = True
                self._web_client = slack.WebClient(token=token)
                self.announcement_channel_name = announcement_channel_name
            else:
                self._enabled = False

            SlackClient.__instance = self

    def announce(self, message):
        '''
        Sends message (str) to the announcement channel.
        '''
        self.send_message(self.announcement_channel_name, message)


    def send_message(self, channel, message):
        '''
        Sends message (str) to specified channel (str). 
        channel can be the name of the channel or the channel id.
        '''
        if not self._enabled:
            return

        self._web_client.chat_postMessage(channel=channel, text=message)


    def create_channel(self, puzzle_name):
        '''
        Returns the assigned channel id (str) if able to create a channel.
        Otherwise, raises an exception.
        '''
        if not self._enabled:
            return None

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

        Unlike send_message, the channel_name should be the name of the channel
        and not a channel ID.
        '''
        if not self._enabled:
            return

        self._web_client.channels_join(channel=channel_name)
