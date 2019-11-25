from django import forms
from .models import Puzzle, MetaPuzzle

class PuzzleForm(forms.Form):
    name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Name of Puzzle"
        })
    )
    url = forms.URLField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "URL"
        })
    )
    is_meta = forms.BooleanField(required=False)


class StatusForm(forms.ModelForm):
    class Meta:
        model = Puzzle
        fields = ["status"]

    status = forms.ChoiceField(
        choices=[(status, status) for status in Puzzle.STATUS_CHOICES],
        widget=forms.Select(attrs={"onChange":'this.form.submit();', 'class': 'form-control form-control-sm'}))


class MetaChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, meta):
         return meta.name

class MetaPuzzleForm(forms.Form):
    meta_select = MetaChoiceField(
        required=False,
        queryset=MetaPuzzle.objects.all(),
        widget=forms.CheckboxSelectMultiple)
