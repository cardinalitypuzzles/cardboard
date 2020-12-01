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
            "is_meta",
        )
