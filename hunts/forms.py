from django import forms

from .models import Hunt, HuntSettings


class HuntForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Name of Hunt"}
        ),
    )
    url = forms.URLField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "URL"})
    )
    start_time = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"class": "form-control", "placeholder": "Start Date"},
            time_attrs={
                "class": "form-control",
                "placeholder": "Start Time (ET, HH:MM, 24 hr)",
            },
        ),
        required=False,
    )
    end_time = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"class": "form-control", "placeholder": "End Date"},
            time_attrs={
                "class": "form-control",
                "placeholder": "End Time (ET, HH:MM, 24 hr)",
            },
        ),
        required=False,
    )

    populate_tags = forms.BooleanField(
        label="Populate hunt with default tags?", initial=True, required=False
    )

    def clean(self):
        data = super().clean()

        if "start_time" in data and "end_time" in data:

            if data["end_time"] and not data["start_time"]:
                raise forms.ValidationError(
                    "Start time must be provided with end time.", code="missing_start"
                )

            if (
                data["start_time"]
                and data["end_time"]
                and data["end_time"] <= data["start_time"]
            ):
                raise forms.ValidationError(
                    "End time must be after start time.", code="end_before_start"
                )

        return data

    class Meta:
        model = Hunt
        fields = ["name", "url", "start_time", "end_time"]


class HuntSettingsForm(forms.ModelForm):
    class Meta:
        model = HuntSettings
        exclude = ["hunt"]
