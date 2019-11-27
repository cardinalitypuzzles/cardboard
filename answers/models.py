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

    def test(self):
        return "test"

    def __update_slack(self, text, status):
        slack_client = SlackClient.getInstance()
        puzzle_channel = self.puzzle.channel
        if status == Answer.PARTIAL:
            slack_client.send_message(puzzle_channel,
                                      "%s is PARTIALLY CORRECT!" %
                                      text.upper())
        elif status == Answer.INCORRECT or status == Answer.CORRECT:
            slack_client.send_message(puzzle_channel, "%s is %s!" %
                                                      (text.upper(), status))

        if status == Answer.CORRECT:
            slack_client.announce("%s has been solved with the answer: "
                                   "\'%s\' Hurray!" % 
                                  (self.puzzle.name, text.upper()))


    def set_status(self, status):
        self._status = status
        self.__update_slack(self.text, status)
        if status == Answer.CORRECT:
            self.puzzle.set_answer(self.text)
        else:
            self.puzzle.clear_answer()
        self.save()

    def get_status(self):
        return self._status



