from django import forms

class AnswerForm(forms.Form):
    text = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Guess"
        })
    )