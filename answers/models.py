from django.db import models

class Answer(models.Model):
    text = models.CharField(max_length=128)
    puzzle = models.ForeignKey('puzzles.Puzzle', on_delete=models.CASCADE, related_name="guesses")
    created_on = models.DateTimeField(auto_now_add=True)
    # for partial answers
    response = ""

    NEW = 'NEW'
    SUBMITTED = 'SUBMITTED'
    CORRECT = 'CORRECT'
    INCORRECT = 'INCORRECT'
    STATUS_CHOICES = [NEW, SUBMITTED, CORRECT, INCORRECT]

    _status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in STATUS_CHOICES],
        default=NEW)



    def set_submitted(self):
        self._status = SUBMITTED


    def set_incorrect(self, response=""):
        self._status = INCORRECT
        # if an answer was incorrectly marked as correct
        if self.puzzle.answer == self.text:
            self.puzzle.answer = None
        self.response = response


    def set_correct(self):
        self._status = CORRECT
        self.puzzle.answer = text


