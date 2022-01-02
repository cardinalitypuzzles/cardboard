import logging
import re
import slack

from django.conf import settings
from puzzles.models import is_unassigned_channel
from slack.errors import SlackApiError


_logger = logging.getLogger(__name__)


class SlackClient:
    """
    This is a wrapper class around the existing slack web client that allows for
    sending messages, creating channels, and joining channels.

    This is a singleton class.
    """

    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if SlackClient.__instance == None:
            SlackClient()
        return SlackClient.__instance

    def __init__(
        self,
        announcement_channel_name="puzzle-announcements",
        answer_queue_channel_name="answer-queue",
    ):
        """ Private constructor. """
        if SlackClient.__instance != None:
            raise Exception(
                "SlackClient is a singleton and should not be "
                "constructed multiple times. Use "
                "SlackClient.getInstance() to access it."
            )

        else:
            token = settings.SLACK_API_TOKEN
            if token:
                self._enabled = True
                self._web_client = slack.WebClient(token=token)
                self.announcement_channel_name = announcement_channel_name
                self.answer_queue_channel_name = answer_queue_channel_name
            else:
                self._enabled = False

            SlackClient.__instance = self

    def announce(self, message):
        """
        Sends message (str) to the announcement channel.
        """
        if not self._enabled:
            return

        self.send_message(self.announcement_channel_name, message)

    def send_message(self, channel, message):
        """
        Sends message (str) to specified channel (str).
        channel can be the name of the channel or the channel id.
        """
        if not self._enabled:
            return

        self._web_client.chat_postMessage(channel=channel, text=message)

    def send_answer_queue_message(self, message):
        if not self._enabled:
            return
        self.send_message(self.answer_queue_channel_name, message)

    def announce_puzzle_creation(
        self, puzzle_name, puzzle_url, channel_id, sheet_url, is_meta=False
    ):
        if not self._enabled:
            return

        puzzle_type = "MetaPuzzle" if is_meta else "Puzzle"
        self.announce(
            "Channel <#%s> created for a new %s titled '%s'!\n"
            "Puzzle link: %s\n"
            "Spreadsheet: %s"
            % (channel_id, puzzle_type, puzzle_name, puzzle_url, sheet_url)
        )
        self.send_message(
            channel_id,
            "This channel has been registered with the "
            "%s titled '%s'. You may submit answers via "
            "the /answer command.\n"
            "Puzzle link: %s\n"
            "Spreadsheet: %s" % (puzzle_type, puzzle_name, puzzle_url, sheet_url),
        )

    def create_or_join_channel(self, puzzle_name):
        """
        Returns the assigned channel_id (str) for the channel created/joined.
        Always returns a unique channel_id which does not already belong to an
        existing channel. If necessary, a suffix may be added to the channel
        name to ensure uniqueness.
        """
        return self.__create_or_join_channel_impl(puzzle_name)

    def __create_channel_name(self, name, suffix):
        """
        Creates a valid Slack channel name `name` by converting all characters
        that are not alphanumeric, hyphen, or underscore to underscores,
        appending a suffix, and ensuring the final name is lowercase and at most
        80 characters.
        """
        suffix = suffix.lower()
        name = re.sub(r"[^a-z0-9_-]", "_", name.lower())
        name = name[: 80 - len(suffix)] + suffix
        return name[:80]

    def __create_or_join_channel_impl(self, puzzle_name, suffix=""):
        """
        Implementation for create_or_join_channel.
        This is a private member because suffix should not be exposed publicly.
        """
        if not self._enabled:
            return None

        def _get_next_suffix(suffix):
            """
            Automatic suffix generation. Suffixes will start with empty string,
            then -2, then -3, etc.
            """
            if not suffix:
                return "2"
            else:
                return str(int(suffix) + 1)

        # Concatenate the puzzle name with a suffix to ensure uniqueness.
        channel_name = self.__create_channel_name(puzzle_name, suffix)

        response = None
        try:
            # If channel exists, it will join. Otherwise, it will create and then
            # join.
            response = self._web_client.channels_join(name=channel_name, validate=True)
        except SlackApiError as e:
            if e.response["error"] == "is_archived":
                self.unarchive_channel(self.get_channel_id(channel_name))
                return self.__create_or_join_channel_impl(channel_name)

        if response and response["ok"]:
            cleaned_channel_name = response["channel"]["name"]
            channel_id = response["channel"]["id"]
            # A puzzle with this channel already exists.
            if not is_unassigned_channel(channel_id):
                return self.__create_or_join_channel_impl(
                    puzzle_name, suffix=_get_next_suffix(suffix)
                )
            return channel_id

        return None

    def get_channel_id(self, channel_name):
        """
        Given a channel name, returns the channel's id. If no such channel exists,
        returns None.
        """
        response = self._web_client.channels_list()
        if response["ok"]:
            return next(
                (
                    channel["id"]
                    for channel in response["channels"]
                    if channel["name"] == channel_name
                ),
                None,
            )
        return None

    def get_channel_name(self, channel_id):
        """
        Given a channel_id (str, e.g. C1H9RESGL), returns the name of that
        human-readable channel name.
        """
        if not self._enabled:
            return channel_id

        response = self._web_client.channels_info(channel=channel_id)
        return response["channel"]["name"]

    def join_channel(self, channel_name):
        """
        Joins channel with given name. Assumes channel_name is valid and
        exists.

        Unlike send_message, the channel_name should be the name of the channel
        and not a channel ID.
        """
        if not self._enabled:
            return

        self._web_client.channels_join(channel=channel_name)

    def get_user_email(self, user_id):
        """
        Given a Slack user id, returns the email address of the user.
        """
        if not self._enabled:
            return user_id

        response = self._web_client.users_info(user=user_id)
        return response["user"]["profile"]["email"]

    def archive_channel(self, channel_id):
        """Archives a channel if it not archived"""
        if not self._enabled:
            return

        try:
            response = self._web_client.channels_info(channel=channel_id)
            if not response["channel"]["is_archived"]:
                self._web_client.channels_archive(channel=channel_id)
        except SlackApiError as e:
            _logger.warn("Encountered error archiving channel %s: %s" % (channel_id, e))

    def unarchive_channel(self, channel_id):
        """Unarchives a channel if it is archived"""
        if not self._enabled:
            return

        try:
            response = self._web_client.channels_info(channel=channel_id)
            if response["ok"] and response["channel"]["is_archived"]:
                self._web_client.channels_unarchive(channel=channel_id)
        except SlackApiError as e:
            _logger.warn(
                "Encountered error unarchiving channel %s: %s" % (channel_id, e)
            )
