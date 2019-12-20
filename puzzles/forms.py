from django import forms
from django.db.models import Q
from .models import Puzzle
from .puzzle_tag import PuzzleTag

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
        }),
        required=False
    )
    is_meta = forms.BooleanField(required=False)


class StatusForm(forms.ModelForm):
    class Meta:
        model = Puzzle
        fields = ["status"]

    status = forms.ChoiceField(
        choices=[(status, status) for status in Puzzle.ALL_STATUSES],
        widget=forms.Select(attrs={"onChange":'this.form.submit();', 'class': 'form-control form-control-sm'}))


class TagForm(forms.Form):
    name = forms.CharField(max_length=128)
    color = forms.ChoiceField(choices=PuzzleTag.VISIBLE_COLOR_CHOICES)


class MetaChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, meta):
         return meta.name

class MetaPuzzleForm(forms.ModelForm):
    class Meta:
        model = Puzzle
        fields = ["metas"]
    metas = MetaChoiceField(
        required=False,
        queryset=Puzzle.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label='')
    def __init__(self, *args, **kwargs):
        super(MetaPuzzleForm, self).__init__(*args, **kwargs)
        self.fields['metas'].queryset = Puzzle.objects.filter(Q(is_meta=True), Q(hunt=self.instance.hunt)).exclude(pk=self.instance.pk)
