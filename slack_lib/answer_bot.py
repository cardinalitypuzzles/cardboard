import os
import slack

from .slack_client import SlackClient

class AnswerBot:
    '''
    Class representing the AnswerBot responsible for listening to answers via
    the Slack channel and updating the slack channel once the answer status is
    changed to SUBMITTED/INCORRECT/CORRECT/PARTIAL.

    Each puzzle model should own an instance of an AnswerBot corresponding to
    the actual slack bot that exists in the corresponding channel.

    Composition is preferred over inheritance because AnswerBot should only
    have power over that single channel.

    root_channel_name must be a valid channel.
    '''
    def __init__(self, token=os.environ["SLACK_BOT_API_TOKEN"],
                 root_channel_name="small-board"):
        # Protected so that callers cannot directly access the slack client.
        # AnswerBot should only have scope over the root_channel_name.
        self._slack_client = SlackClient(token, root_channel_name)
        self._slack_client.join_channel(root_channel_name)

    def UpdateStatus(self, new_status):
