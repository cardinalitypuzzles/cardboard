import os
import slack

from .slack_client import SlackClient

class AnswerBot:
    '''
    Class representing the AnswerBot responsible for listening to answers via
    the Slack channel and updating the slack channel once the answer status is
    changed to INCORRECT/CORRECT/PARTIAL.

    Each puzzle model should own an instance of an AnswerBot corresponding to
    the actual slack bot that exists in the corresponding channel.

    Composition is preferred over inheritance because AnswerBot should only
    have power over that single channel.

    root_channel_name must be a valid channel assigned to a puzzle.
    '''
    def __init__(self, token=os.environ["SLACK_BOT_API_TOKEN"],
                 root_channel_name="small-board"):
        # Protected so that callers cannot directly access the slack client.
        # AnswerBot should only have be able to publish in root_channel_name.
        self._slack_client = SlackClient(token, root_channel_name)
        self.root_channel_name = root_channel_name
        self._slack_client.join_channel(root_channel_name)

    def UpdateStatus(self, answer, new_status, supplementary_msg=""):
        '''
        Upon change in status to CORRECT, INCORRECT, or PARTIAL, publish an
        update to the root slack channel.
        '''
        if new_status == 'CORRECT' or new_status == 'INCORRECT':
            self._slack_client.send_message(self.root_channel_name, "Answer " +
                                            answer + " is " + new_status "!")
        elif new_status == 'PARTIAL':
            self._slack_client.send_message(self.root_channel_name, "Answer " +
                                            answer + " is partially correct." +
                                            " Supplementary msg: " +
                                            supplementary_msg)
            
