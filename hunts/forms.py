from datetime import timedelta

from django import forms

from google_api_lib.utils import extract_google_id

from .models import Hunt, HuntSettings


class SecondsDurationField(forms.IntegerField):
    """Form field that edits a DurationField as an integer number of seconds."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("min_value", 0)
        super().__init__(*args, **kwargs)
        self.widget.attrs.setdefault("min", 0)

    def prepare_value(self, value):
        if isinstance(value, timedelta):
            return int(value.total_seconds())
        return value

    def clean(self, value):
        seconds = super().clean(value)
        if seconds is None:
            return None
        return timedelta(seconds=seconds)


class HuntForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-sm",
                "placeholder": "Name of Hunt",
            }
        ),
    )
    url = forms.URLField(
        widget=forms.TextInput(
            attrs={"class": "form-control form-control-sm", "placeholder": "URL"}
        )
    )
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "class": "form-control form-control-sm",
                "type": "datetime-local",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ],
        label="Start Time (ET)",
        required=False,
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "class": "form-control form-control-sm",
                "type": "datetime-local",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=[
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ],
        label="End Time (ET)",
        required=False,
    )

    populate_tags = forms.BooleanField(
        label="Populate hunt with default tags?",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
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
    field_order = ["active_user_lookback", "answer_queue_enabled"]
    GOOGLE_DRIVE_FIELDS = (
        "google_drive_folder_id",
        "google_sheets_template_file_id",
        "google_sheets_template_folder_id",
        "google_drive_human_url",
    )
    DISCORD_FIELDS = (
        "create_channel_by_default",
        "discord_guild_id",
        "discord_puzzle_announcements_channel_id",
        "discord_metas_category",
        "discord_unassigned_text_category",
        "discord_unassigned_voice_category",
        "discord_archive_category",
        "discord_devs_role",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control form-control-sm"
            if name in self.DISCORD_FIELDS and field.label:
                label = field.label.removeprefix("Discord ")
                field.label = label[0].upper() + label[1:]
        self.fields["google_drive_human_url"].widget = forms.TextInput(
            attrs={"class": "form-control form-control-sm"}
        )

    def cardboard_fields(self):
        grouped = set(self.GOOGLE_DRIVE_FIELDS) | set(self.DISCORD_FIELDS)
        return [self[name] for name in self.fields if name not in grouped]

    def google_drive_fields(self):
        return [self[name] for name in self.GOOGLE_DRIVE_FIELDS]

    def discord_fields(self):
        return [self[name] for name in self.DISCORD_FIELDS]

    def _clean_google_id_field(self, field_name):
        value = self.cleaned_data.get(field_name, "")
        try:
            return extract_google_id(value)
        except ValueError as e:
            raise forms.ValidationError(str(e))

    def clean_google_drive_folder_id(self):
        return self._clean_google_id_field("google_drive_folder_id")

    def clean_google_sheets_template_file_id(self):
        return self._clean_google_id_field("google_sheets_template_file_id")

    def clean_google_sheets_template_folder_id(self):
        return self._clean_google_id_field("google_sheets_template_folder_id")

    class Meta:
        model = HuntSettings
        exclude = ["hunt"]
        field_classes = {"active_user_lookback": SecondsDurationField}
