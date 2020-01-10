from django import forms
from .models import Answer

class AnswerForm(forms.Form):
    text = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-sm",
            "placeholder": "Enter Guess"
        })
    )

class UpdateAnswerStatusForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["status"]

    status = forms.ChoiceField(
        choices=[(status, status) for status in Answer.STATUS_CHOICES],
        widget=forms.Select(attrs={"onChange": "this.form.submit();",
                                   "class": "form-control form-control-sm"}))

class UpdateAnswerNotesForm(forms.Form):
    text = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-sm",
            "placeholder": "Enter notes here"
        }),
        required=False,
    )
