from django.db import IntegrityError
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from answers.models import Answer
from hunts.models import Hunt
from puzzles.models import Puzzle, PuzzleModelError
from .serializers import AnswerSerializer, HuntSerializer, PuzzleSerializer
from google_api_lib.google_api_client import GoogleApiClient

import logging
import re

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

    def __sanitize_answer(self, answer):
        """Strips whitespace and converts to uppercase."""
        return re.sub(r"\s", "", answer).upper()

    def get_queryset(self):
        puzzle_id = self.kwargs["puzzle_id"]
        return Answer.objects.filter(puzzle__id=puzzle_id)

    def create(self, request, **kwargs):
        puzzle = None
        with transaction.atomic():
            hunt = get_object_or_404(Hunt, pk=self.kwargs["hunt_id"])
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            text = self.__sanitize_answer(serializer.validated_data["text"])
            answer, created = Answer.objects.get_or_create(text=text, puzzle=puzzle)
            # If answer has already been added
            if not created:
                return Response(
                    {
                        "detail": '"An identical answer has already been submitted for that puzzle."'
                    },
                    status=400,
                )
            if hunt.answer_queue_enabled:
                puzzle.status = Puzzle.PENDING
            else:
                # If no answer queue, we assume that the submitted answer is the
                # correct answer.
                puzzle.status = Puzzle.SOLVED
                answer.status = Answer.CORRECT
                puzzle.answer = answer.text
                answer.save()
            puzzle.save()

        return Response(PuzzleSerializer(puzzle).data)

    def destroy(self, request, pk=None, **kwargs):
        puzzle = None
        with transaction.atomic():
            hunt = get_object_or_404(Hunt, pk=self.kwargs["hunt_id"])
            answer = self.get_object()
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            answer.delete()
            # If a SOLVED puzzle has no more correct answers, revert status to SOLVING.
            if (
                not puzzle.guesses.filter(status=Answer.CORRECT)
                and puzzle.status == Puzzle.SOLVED
            ) or (not puzzle.guesses.all() and puzzle.status == Puzzle.PENDING):
                puzzle.status = Puzzle.SOLVING
                puzzle.save()

        return Response(PuzzleSerializer(puzzle).data)

    def partial_update(self, request, p=None, **kwargs):
        puzzle = None
        try:
            with transaction.atomic():
                answer = self.get_object()
                puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
                serializer = self.get_serializer(
                    answer, data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                text = self.__sanitize_answer(serializer.validated_data["text"])
                answer.update(text)
                puzzle.save()
        except IntegrityError as e:
            msg = str(e)
            if 'unique constraint' in e.message:
                msg = "An identical answer has already been submitted for that puzzle."
            return Response(
                {"detail": msg},
                status=400,
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

            puzzle = serializer.save(sheet=sheet, hunt=hunt)

            if google_api_client:
                transaction.on_commit(
                    lambda: google_api_client.add_puzzle_link_to_sheet(
                        puzzle_url, sheet
                    )
                )

        return Response(PuzzleSerializer(puzzle).data)
