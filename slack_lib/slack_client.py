import os
import slack

from puzzles.models import *

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

    def announce_puzzle_creation(self, puzzle_name, channel_id):
        channel_name = self.get_channel_name(channel_id)
        self.announce(
                      "Channel %s created for puzzle titled %s!" %
                      (channel_name, puzzle_name))
        self.send_message(channel_id, 
                      "This channel has been registered with the "
                      "puzzle titled %s. You may submit answers via "
                      "the /answer command." % puzzle_name)

    def create_or_join_channel(self, puzzle_name):
        '''
        Returns the assigned channel_id (str) for the channel created/joined.
        Always returns a unique channel_id which does not already belong to an
        existing channel. If necessary, a suffix may be added to the channel
        name to ensure uniqueness.
        '''
        return self.__create_or_join_channel_impl(puzzle_name)


    def __create_or_join_channel_impl(self, puzzle_name, suffix=""):
        '''
        Implementation for create_or_join_channel.
        This is a private member because suffix should not be exposed publicly.
        '''
        if not self._enabled:
            return None

        def _get_next_suffix(suffix):
            '''
            Automatic suffix generation. Suffixes will start with empty string,
            then -2, then -3, etc.
            '''
            if not suffix:
                return "2"
            else:
                return str(int(suffix) + 1)

        # Concatenate the puzzle name with a suffix to ensure uniqueness.
        uncleaned_channel_name = "%s-%s" % (puzzle_name, suffix) if suffix else puzzle_name
        # By setting validate=False, the client will automatically clean up
        # special characters and make it fit under 80 characters.
        response = self._web_client.channels_join(name=uncleaned_channel_name,
                                                  validate=False)

        if response["ok"]:
            cleaned_channel_name = response["channel"]["name"]
            channel_id = response["channel"]["id"]
            # A puzzle with this channel already exists.
            if not is_unassigned_channel(channel_id):
                return self.__create_or_join_channel_impl(puzzle_name,
                           suffix=_get_next_suffix(suffix))
            return channel_id


    def get_channel_name(self, channel_id):
        '''
        Given a channel_id (str, e.g. C1H9RESGL), returns the name of that
        human-readable channel name.
        '''
        response = self._web_client.channels_info(channel=channel_id)
        return response["channel"]["name"]


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
