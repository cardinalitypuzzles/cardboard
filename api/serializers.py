from rest_framework import serializers
from hunts.models import Hunt
from puzzles.models import Puzzle


class HuntSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hunt
        fields = ("id", "name", "active")


class PuzzleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return [{"name": tag.name, "color": tag.color} for tag in obj.tags.all()]

    def validate(self, data, *args, **kwargs):
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
        if not get_merged("is_meta") and len(self.instance.feeders.all()) > 0:
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
