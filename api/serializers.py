from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from answers.models import Answer
from chat.models import ChatRoom
from hunts.models import Hunt
from puzzles.models import Puzzle, PuzzleTag

from url_normalize import url_normalize

import re


class HuntSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hunt
        fields = ("id", "name", "active")


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


class PuzzleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuzzleTag
        fields = ("id", "name", "color", "is_meta")

        read_only_fields = ("id", "is_meta")


class PuzzleSerializer(serializers.ModelSerializer):
    chat_room = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField(required=False)
    guesses = serializers.SerializerMethodField()
    # Have to specify this explicitly for validate_url to run
    url = serializers.URLField()
    hunt_id = serializers.PrimaryKeyRelatedField(
        read_only=True, default=CurrentHuntDefault()
    )

    def get_chat_room(self, obj):
        return ChatRoomSerializer(obj.chat_room).data

    def get_guesses(self, obj):
        # Show only correct guesses.
        guesses = obj.guesses.filter(status=Answer.CORRECT)
        return AnswerSerializer(guesses, many=True).data

    def get_tags(self, instance):
        tags = instance.tags.all().order_by("color", "name")
        return PuzzleTagSerializer(tags, many=True).data

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
            "sheet",
            "chat_room",
            "status",
            "tags",
            "guesses",
            "metas",
            "feeders",
            "is_meta",
        )

        read_only_fields = (
            "id",
            "hunt_id",
            "sheet",
            "chat_room",
            "guesses",
            "tags",
            "metas",
            "feeders",
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
