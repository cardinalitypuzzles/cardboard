from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from answers.models import Answer
from hunts.models import Hunt
from puzzles.models import Puzzle

from url_normalize import url_normalize


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


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ("text", )


class PuzzleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    # Have to specify this explicitly for validate_url to run
    url = serializers.CharField()
    hunt_id = serializers.PrimaryKeyRelatedField(
        read_only=True, default=CurrentHuntDefault()
    )

    def get_tags(self, obj):
        return [{"name": tag.name, "color": tag.color} for tag in obj.tags.all()]

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

        # Feeders can't have feeders
        feeders_query = get_merged("feeders")
        feeders = (feeders_query and feeders_query.all()) or []
        if not get_merged("is_meta") and len(feeders) > 0:
            raise serializers.ValidationError(
                "Puzzle must be a meta to have puzzles assigned."
            )
        # Answers mean solves
        if get_merged("status") == "SOLVED" and not get_merged("answer"):
            raise serializers.ValidationError("Solved puzzles must have answers.")
        if get_merged("answer") and get_merged("status") != "SOLVED":
            raise serializers.ValidationError("Puzzles with answers are solved.")

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
            "status",
            "answer",
            "tags",
            "metas",
            "feeders",
            "is_meta",
        )

        read_only_fields = (
            "id",
            "hunt_id",
            "sheet",
            "answer",
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
