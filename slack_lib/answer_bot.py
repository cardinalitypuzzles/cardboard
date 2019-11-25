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
    '''
    def __init__(self, token=os.environ["SLACK_BOT_API_TOKEN"],
                 root_channel_name="small-board"):
        # Protected so that callers cannot directly access the slack client.
        # AnswerBot should not have the full power 
        self._slack_client = SlackClient(token, root_channel_name)

    def UpdateStatus(self, new_status):
