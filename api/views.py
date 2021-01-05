from django.conf import settings
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from answers.models import Answer
from chat.models import ChatRoom
from hunts.models import Hunt
from puzzles.models import Puzzle, PuzzleModelError, PuzzleTag, is_ancestor
from .serializers import (
    AnswerSerializer,
    HuntSerializer,
    PuzzleSerializer,
    PuzzleTagSerializer,
)
from google_api_lib.google_api_client import GoogleApiClient

import logging

logger = logging.getLogger(__name__)

# Right now IsAuthenticated ensures that only logged-in users
# can use the API, but it does not test permissions beyond that.
# TODO: per-hunt user permissions/authentication


class HuntAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        hunt = get_object_or_404(Hunt, pk=pk)
        serializer = HuntSerializer(hunt)
        return Response(serializer.data)


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSerializer

    @staticmethod
    def __update_meta_sheets_for_feeder(feeder):
        for meta in feeder.metas.all():
            GoogleApiClient.update_meta_sheet_feeders(meta)

    def get_queryset(self):
        puzzle_id = self.kwargs["puzzle_id"]
        return Answer.objects.filter(puzzle__id=puzzle_id)

    def create(self, request, **kwargs):
        puzzle = None
        with transaction.atomic():
            hunt = get_object_or_404(Hunt, pk=self.kwargs["hunt_id"])
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            serializer = self.get_serializer(
                data=request.data, context={"puzzle": puzzle}
            )
            serializer.is_valid(raise_exception=True)
            text = serializer.validated_data["text"]
            answer = Answer(text=text, puzzle=puzzle)
            if hunt.answer_queue_enabled:
                puzzle.status = Puzzle.PENDING
            else:
                # If no answer queue, we assume that the submitted answer is the
                # correct answer.
                puzzle.status = Puzzle.SOLVED
                answer.status = Answer.CORRECT
                puzzle.answer = answer.text
                puzzle.chat_room.archive_channels()
                answer.save()
                transaction.on_commit(
                    lambda: AnswerViewSet.__update_meta_sheets_for_feeder(puzzle)
                )
            puzzle.save()

        return Response(PuzzleSerializer(puzzle).data)

    def destroy(self, request, pk=None, **kwargs):
        puzzle = None
        with transaction.atomic():
            answer = self.get_object()
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            answer.delete()
            # If a SOLVED puzzle has no more correct answers, revert status to SOLVING.
            if (
                not puzzle.guesses.filter(status=Answer.CORRECT)
                and puzzle.status == Puzzle.SOLVED
            ) or (not puzzle.guesses.all() and puzzle.status == Puzzle.PENDING):
                puzzle.status = Puzzle.SOLVING
                puzzle.chat_room.unarchive_channels()
                puzzle.save()

            transaction.on_commit(
                lambda: AnswerViewSet.__update_meta_sheets_for_feeder(puzzle)
            )

        return Response(PuzzleSerializer(puzzle).data)

    def partial_update(self, request, pk=None, **kwargs):
        super().partial_update(request, pk, **kwargs)

        puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
        transaction.on_commit(
            lambda: AnswerViewSet.__update_meta_sheets_for_feeder(puzzle)
        )

        return Response(PuzzleSerializer(puzzle).data)


class PuzzleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PuzzleSerializer

    def get_queryset(self):
        hunt_id = self.kwargs["hunt_id"]
        return (
            Puzzle.objects.filter(hunt__id=hunt_id)
            .prefetch_related("metas")
            .prefetch_related("tags")
            .prefetch_related("chat_room")
            .prefetch_related("guesses")
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
        try:
            with transaction.atomic():
                puzzle = self.get_object()
                serializer = self.get_serializer(
                    puzzle, data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                data = serializer.validated_data
                puzzle.update_metadata(
                    new_name=data.get("name", puzzle.name),
                    new_url=data.get("url", puzzle.url),
                    new_is_meta=data.get("is_meta", puzzle.is_meta),
                )
                if "status" in data:
                    puzzle.status = data["status"]
                    puzzle.save()
        except PuzzleModelError as e:
            return Response(
                {"detail": str(e)},
                status=400,
            )

        return Response(PuzzleSerializer(puzzle).data)

    def create(self, request, **kwargs):
        puzzle = None
        with transaction.atomic():
            hunt = get_object_or_404(Hunt, pk=self.kwargs["hunt_id"])
            serializer = self.get_serializer(data=request.data, context={"hunt": hunt})
            serializer.is_valid(raise_exception=True)

            name = serializer.validated_data["name"]
            puzzle_url = serializer.validated_data["url"]
            sheet = None
            google_api_client = GoogleApiClient.getInstance()
            if google_api_client:
                sheet = google_api_client.create_google_sheets(name)
            else:
                logger.warn("Sheet not created for puzzle %s" % name)

            if settings.CHAT_DEFAULT_SERVICE:
                chat_room = ChatRoom.objects.create(
                    service=settings.CHAT_DEFAULT_SERVICE, name=name
                )
                chat_room.create_channels()
            else:
                logger.warn("Chat room not created for puzzle %s" % name)
                chat_room = None

            puzzle = serializer.save(sheet=sheet, hunt=hunt, chat_room=chat_room)

            if google_api_client:
                transaction.on_commit(
                    lambda: google_api_client.add_puzzle_link_to_sheet(
                        puzzle_url, sheet
                    )
                )

        return Response(PuzzleSerializer(puzzle).data)


class PuzzleTagViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PuzzleTagSerializer

    def get_queryset(self):
        hunt_id = self.kwargs["hunt_id"]
        return PuzzleTag.objects.filter(hunt__id=hunt_id)

    def destroy(self, request, pk=None, **kwargs):
        puzzle = None
        with transaction.atomic():
            tag = self.get_object()
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            if puzzle.name == tag.name:
                return Response(
                    {
                        "detail": "You cannot remove a meta's tag (%s) from itself"
                        % tag.name
                    },
                    status=400,
                )
            if tag.is_meta:
                meta = Puzzle.objects.get(name=tag.name, hunt=puzzle.hunt)
                # the post m2m hook will remove tag
                puzzle.metas.remove(meta)
            else:
                puzzle.tags.remove(tag)

            # clear db of dangling tags
            if not tag.puzzles.exists():
                tag.delete()

        return Response(PuzzleSerializer(puzzle).data)

    def create(self, request, **kwargs):
        puzzle = None
        with transaction.atomic():
            hunt = get_object_or_404(Hunt, pk=self.kwargs["hunt_id"])
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            serializer = self.get_serializer(data=request.data, context={"hunt": hunt})
            serializer.is_valid(raise_exception=True)
            tag_name, tag_color = (
                serializer.validated_data["name"],
                serializer.validated_data["color"],
            )
            tag, _ = PuzzleTag.objects.update_or_create(
                name=tag_name,
                hunt=puzzle.hunt,
                defaults={"color": tag_color},
            )
            if tag.is_meta:
                metapuzzle = get_object_or_404(Puzzle, name=tag.name, hunt=puzzle.hunt)
                if is_ancestor(puzzle, metapuzzle):
                    return Response(
                        {
                            "detail": '"Unable to assign metapuzzle since doing so would introduce a meta-cycle."'
                        },
                        status=400,
                    )
                # the post m2m hook will add tag
                puzzle.metas.add(metapuzzle)
            else:
                puzzle.tags.add(tag)

            return Response(PuzzleSerializer(puzzle).data)
