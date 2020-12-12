from django.db import transaction
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

    def destroy(self, request, pk=None, **kwargs):
        metas = None
        with transaction.atomic():
            puzzle = self.get_object()
            if not puzzle.can_delete():
                return Response(
                    {
                        "detail": "Metapuzzles can only be deleted or made non-meta if no "
                        "other puzzles are assigned to it."
                    },
                    status=400,
                )
            puzzle.delete()

        return Response({})

    def partial_update(self, request, pk=None, **kwargs):
        puzzle = None
        with transaction.atomic():
            puzzle = self.get_object()
            serializer = self.get_serializer(puzzle, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            puzzle.update_metadata(
                new_name=data["name"], new_url=data["url"], new_is_meta=data["is_meta"]
            )

        return Response(PuzzleSerializer(puzzle).data)
