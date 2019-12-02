from django.db import models

from slack_lib.slack_client import SlackClient

class Answer(models.Model):
    text = models.CharField(max_length=128)
    puzzle = models.ForeignKey('puzzles.Puzzle', on_delete=models.CASCADE, related_name="guesses")
    created_on = models.DateTimeField(auto_now_add=True)
    # for partial answers
    response = models.TextField(default="")

    NEW = 'NEW'
    SUBMITTED = 'SUBMITTED'
    CORRECT = 'CORRECT'
    INCORRECT = 'INCORRECT'
    PARTIAL = 'PARTIAL'
    STATUS_CHOICES = [NEW, SUBMITTED, CORRECT, INCORRECT, PARTIAL]

    _status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in STATUS_CHOICES],
        default=NEW)

    def __str__(self):
        return '{}: "{}" ({})'.format(self.puzzle.name, self.text, self._status)

    def __update_slack_with_puzzle_status(self, status):
        slack_client = SlackClient.getInstance()
        puzzle_channel = self.puzzle.channel
        if status == Answer.PARTIAL:
            slack_client.send_message(puzzle_channel,
                                      "%s is PARTIALLY CORRECT!" %
                                      self.text.upper())
        elif status == Answer.INCORRECT or status == Answer.CORRECT:
            slack_client.send_message(puzzle_channel, "%s is %s!" %
                                                      (self.text.upper(), status))

        if status == Answer.CORRECT:
            slack_client.announce("%s has been solved with the answer: "
                                   "\'%s\' Hurray!" %
                                  (self.puzzle.name, self.text.upper()))


    def __update_slack_with_puzzle_notes(self, notes):
        slack_client = SlackClient.getInstance()
        puzzle_channel = self.puzzle.channel
        slack_client.send_message(puzzle_channel,
                                  "The operator has added an update regarding the answer "
                                   "\'%s\'. Note: \'%s\'" % (self.text.upper(), notes))

    def set_status(self, status):
        self._status = status
        self.__update_slack_with_puzzle_status(status)
        if status == Answer.CORRECT:
            self.puzzle.set_answer(self.text)
        else:
            self.puzzle.clear_answer()
        self.save()

    def get_status(self):
        return self._status

    # TODO(asdfryan): Migrate response to notes.
    def set_notes(self, notes):
        self.response = notes
        self.__update_slack_with_puzzle_notes(notes)
        self.save()

    def get_notes(self):
        return self.response
