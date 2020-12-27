from django.db import models


class Answer(models.Model):
    text = models.CharField(max_length=128)
    puzzle = models.ForeignKey(
        "puzzles.Puzzle", on_delete=models.CASCADE, related_name="guesses"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    # for partial answers
    response = models.TextField(default="")

    NEW = "NEW"
    SUBMITTED = "SUBMITTED"
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    PARTIAL = "PARTIAL"
    STATUS_CHOICES = [NEW, SUBMITTED, CORRECT, INCORRECT, PARTIAL]

    # Only applicable if answer queue is enabled. If answer queue is disabled, all
    # created answers should be CORRECT.
    status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in STATUS_CHOICES],
        default=NEW,
    )

    def __str__(self):
        return '{}: "{}" ({})'.format(self.puzzle.name, self.text, self.status)

    def set_status(self, status):
        self.status = status
        self.save()
        if status == Answer.CORRECT:
            self.puzzle.set_answer(self.text)
        else:
            self.puzzle.clear_answer(self.text)

    def get_status(self):
        return self.status

    # TODO(asdfryan): Migrate response to notes.
    def set_notes(self, notes):
        self.response = notes
        self.save()

    def get_notes(self):
        return self.response

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["text", "puzzle"], name="unique_answer_text_per_puzzle"
            ),
        ]
