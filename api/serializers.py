from rest_framework import serializers
from hunts.models import Hunt


class HuntSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hunt
        fields = ("id", "name", "active")
