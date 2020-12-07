from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from hunts.models import Hunt
from puzzles.models import Puzzle
from .serializers import HuntSerializer, PuzzleSerializer

# Right now IsAuthenticated ensures that only logged-in users
# can use the API, but it does not test permissions beyond that.
# TODO: per-hunt user permissions/authentication


class HuntAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        hunt = get_object_or_404(Hunt, pk=pk)
        serializer = HuntSerializer(hunt)
        return Response(serializer.data)


class PuzzleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PuzzleSerializer

    def get_queryset(self):
        hunt_id = self.kwargs["hunt_id"]
        return (
            Puzzle.objects.filter(hunt__id=hunt_id)
            .prefetch_related("metas")
            .prefetch_related("tags")
        )
