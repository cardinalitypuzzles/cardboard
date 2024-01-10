import datetime
import re

from dateutil import tz
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from url_normalize import url_normalize

from answers.models import Answer
from chat.models import ChatRoom
from hunts.models import Hunt
from puzzles.models import Puzzle, PuzzleTag


class PuzzleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuzzleTag
        fields = (
            "id",
            "name",
            "color",
            "is_meta",
            "is_high_pri",
            "is_low_pri",
            "is_location",
        )

        read_only_fields = ("id", "is_meta", "is_high_pri", "is_low_pri", "is_location")


class HuntSerializer(serializers.ModelSerializer):
    has_drive = serializers.SerializerMethodField()
    puzzle_tags = PuzzleTagSerializer(required=False, many=True)

    def get_has_drive(self, obj):
        return bool(obj.settings.google_drive_human_url)

    class Meta:
        model = Hunt
        fields = ("id", "name", "active", "url", "has_drive", "puzzle_tags")


class CurrentHuntDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context.get("hunt")

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)


class CurrentPuzzleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context.get("puzzle")

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)


class AnswerSerializer(serializers.ModelSerializer):
    # Have to specify this explicitly for validate_text to run.
    text = serializers.CharField()
    puzzle_id = serializers.PrimaryKeyRelatedField(
        read_only=True, default=CurrentPuzzleDefault()
    )

    def __sanitize_answer(self, answer):
        """Strips whitespace and converts to uppercase."""
        return re.sub(r"\s", "", answer).upper()

    def validate_text(self, text):
        return self.__sanitize_answer(text)

    class Meta:
        model = Answer
        fields = (
            "id",
            "text",
            "puzzle_id",
        )
        read_only_fields = (
            "id",
            "puzzle_id",
        )
        validators = (
            UniqueTogetherValidator(
                queryset=Answer.objects.all(),
                fields=["text", "puzzle_id"],
                message="There is already an identical answer for that puzzle.",
            ),
        )


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = (
            "text_channel_url",
            "audio_channel_url",
        )
        read_only_fields = (
            "text_channel_url",
            "audio_channel_url",
        )


class PuzzleSerializer(serializers.ModelSerializer):
    chat_room = ChatRoomSerializer(required=False)
    tags = PuzzleTagSerializer(required=False, many=True)
    guesses = serializers.SerializerMethodField()
    has_sheet = serializers.SerializerMethodField()
    # Have to specify this explicitly for validate_url to run
    url = serializers.CharField()
    hunt_id = serializers.PrimaryKeyRelatedField(
        read_only=True, default=CurrentHuntDefault()
    )
    recent_editors = serializers.SerializerMethodField()
    top_editors = serializers.SerializerMethodField()
    last_edited_on = serializers.SerializerMethodField()

    def get_guesses(self, obj):
        # Show only correct guesses.
        if hasattr(obj, "_prefetched_correct_answers"):
            return AnswerSerializer(obj._prefetched_correct_answers, many=True).data

        guesses = obj.guesses.filter(status=Answer.CORRECT)
        return AnswerSerializer(guesses, many=True).data

    def get_has_sheet(self, obj):
        return bool(obj.sheet)

    def get_recent_editors(self, obj):
        if hasattr(obj, "_recent_editors"):
            return sorted([str(user) for user in obj._recent_editors])

        before_time = (
            datetime.datetime.now(tz=tz.UTC) - obj.hunt.settings.active_user_lookback
        )

        recent_editors = obj.active_users.filter(
            puzzle_activities__puzzle_id=obj.id,
            puzzle_activities__last_edit_time__gt=before_time,
        ).all()
        return sorted([str(user) for user in recent_editors])

    def get_top_editors(self, obj):
        # distinct and order_by with a related model interact oddly and result in non-distinct results
        if hasattr(obj, "_top_editors"):
            top_editors_with_duplicates = obj._top_editors
        else:
            top_editors_with_duplicates = obj.active_users.filter(
                puzzle_activities__num_edits__gt=5
            ).order_by("-puzzle_activities__num_edits")

        top_editors = []
        for user in top_editors_with_duplicates:
            if str(user) not in top_editors:
                top_editors.append(str(user))

            if len(top_editors) >= 5:
                break

        return top_editors

    def get_last_edited_on(self, obj):
        puzzle_activities = obj.puzzle_activities.all()
        if len(puzzle_activities) > 0:
            return max(
                [activity.last_edit_time for activity in obj.puzzle_activities.all()]
            )
        else:
            return None

    def validate_url(self, url):
        return url_normalize(url)

    def validate(self, data, *args, **kwargs):
        data = super().validate(data, *args, **kwargs)

        # The django rest framework validation is super clunky for validating
        # partial updates; we need to merge new values with existing ones
        # ourselves annoyingly.
        def get_merged(attr):
            if attr in data:
                return data[attr]
            if self.instance and hasattr(self.instance, attr):
                return getattr(self.instance, attr)
            return None

        # Non-metas can't have feeders
        feeders_query = get_merged("feeders")
        feeders = (feeders_query and feeders_query.all()) or []
        if not get_merged("is_meta") and len(feeders) > 0:
            raise serializers.ValidationError(
                "Puzzle must be a meta to have puzzles assigned."
            )
        # Solved puzzles must have at least one correct guess, but not
        # necessarily the other way around.
        if get_merged("status") == "SOLVED" and not get_merged("guesses"):
            raise serializers.ValidationError(
                "Solved puzzles must have at least one correct guess."
            )

        return data

    class Meta:
        model = Puzzle
        fields = (
            "id",
            "name",
            "hunt_id",
            "url",
            "notes",
            "has_sheet",
            "chat_room",
            "status",
            "tags",
            "guesses",
            "metas",
            "feeders",
            "is_meta",
            "created_on",
            "recent_editors",
            "top_editors",
            "last_edited_on",
        )

        read_only_fields = (
            "id",
            "hunt_id",
            "has_sheet",
            "chat_room",
            "guesses",
            "tags",
            "metas",
            "feeders",
            "created_on",
            "recent_editors",
            "top_editors",
            "last_edited_on",
        )

        validators = (
            UniqueTogetherValidator(
                queryset=Puzzle.objects.all(),
                fields=["hunt_id", "name"],
                message="There is already a puzzle with this name.",
            ),
            UniqueTogetherValidator(
                queryset=Puzzle.objects.all(),
                fields=["hunt_id", "url"],
                message="There is already a puzzle with this URL.",
            ),
        )
