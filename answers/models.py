from django.db import models

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
    STATUS_CHOICES = [NEW, SUBMITTED, CORRECT, INCORRECT]

    _status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in STATUS_CHOICES],
        default=NEW)

    def test(self):
        return "test"

    def set_status(self, status):
        self._status = status
        if status == Answer.CORRECT:
            self.puzzle.set_answer(self.text)
        else:
            self.puzzle.clear_answer()
        self.save()

    def get_status(self):
        return self._status



