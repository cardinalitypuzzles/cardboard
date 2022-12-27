from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
import google_api_lib.tasks
import chat.tasks

import logging

logger = logging.getLogger(__name__)

# Right now IsAuthenticated ensures that only logged-in users
# can use the API, but it does not test permissions beyond that.
# TODO: per-hunt user permissions/authentication


class HuntViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HuntSerializer
    queryset = Hunt.objects.all()


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSerializer

    @staticmethod
    def _maybe_update_meta_sheets_for_feeder(feeder):
        if google_api_lib.enabled():
            for meta in feeder.metas.all():
                google_api_lib.tasks.update_meta_and_metameta_sheets_delayed(meta)

    def get_queryset(self):
        puzzle_id = self.kwargs["puzzle_id"]
        return Answer.objects.filter(puzzle__id=puzzle_id)

    @staticmethod
    def _maybe_update_sheets_title(puzzle):

        if google_api_lib.enabled() and puzzle.sheet:
            if puzzle.is_solved():
                solve_label = "BACKSOLVED" if puzzle.is_backsolved() else "SOLVED"
                answers = ", ".join(puzzle.correct_answers())

                google_api_lib.tasks.rename_sheet.delay(
                    sheet_url=puzzle.sheet,
                    name=f"[{solve_label}: {answers}] {puzzle.name}",
                )
            else:
                google_api_lib.tasks.rename_sheet.delay(
                    sheet_url=puzzle.sheet, name=puzzle.name
                )

    def create(self, request, **kwargs):
        puzzle = None
        with transaction.atomic():
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            serializer = self.get_serializer(
                data=request.data, context={"puzzle": puzzle}
            )
            serializer.is_valid(raise_exception=True)
            text = serializer.validated_data["text"]
            answer = Answer(text=text, puzzle=puzzle)
            if puzzle.hunt.settings.answer_queue_enabled:
                puzzle.status = Puzzle.PENDING
            else:
                # If no answer queue, we assume that the submitted answer is the
                # correct answer.
                puzzle.status = Puzzle.SOLVED
                answer.status = Answer.CORRECT
                puzzle.answer = answer.text
                if puzzle.chat_room:
                    transaction.on_commit(
                        lambda: chat.tasks.handle_puzzle_solved.delay(
                            puzzle.id, answer.text
                        )
                    )
                    transaction.on_commit(
                        lambda: chat.tasks.cleanup_puzzle_channels.apply_async(
                            args=(puzzle.id,), countdown=1800  # clean up in 30 minutes
                        )
                    )
                answer.save()
                transaction.on_commit(
                    lambda: AnswerViewSet._maybe_update_meta_sheets_for_feeder(puzzle)
                )
                transaction.on_commit(
                    lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
                )

            puzzle.save()

        return Response(PuzzleSerializer(puzzle).data)

    def destroy(self, request, pk=None, **kwargs):
        puzzle = None
        with transaction.atomic():
            answer = self.get_object()
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            was_backsolved = puzzle.is_backsolved()
            answer.delete()
            # If a SOLVED puzzle has no more correct answers, revert status to SOLVING.
            if (
                not puzzle.guesses.filter(status=Answer.CORRECT)
                and puzzle.status == Puzzle.SOLVED
            ) or (not puzzle.guesses.all() and puzzle.status == Puzzle.PENDING):
                puzzle.status = Puzzle.SOLVING
                if puzzle.chat_room:
                    transaction.on_commit(
                        lambda: chat.tasks.handle_puzzle_unsolved.delay(puzzle.id)
                    )
                elif settings.CHAT_DEFAULT_SERVICE:
                    # recreate chat if they had already been cleaned up from being marked as SOLVED
                    transaction.on_commit(
                        lambda: chat.tasks.create_chat_for_puzzle.delay(puzzle.id)
                    )
                # remove backsolve tag if puzzle is no longer solved
                if was_backsolved:
                    backsolve_tag = PuzzleTag.objects.filter(
                        name=PuzzleTag.BACKSOLVED, hunt=puzzle.hunt
                    )

                    puzzle.tags.remove(backsolve_tag[0])

                puzzle.save()

            transaction.on_commit(
                lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
            )
            transaction.on_commit(
                lambda: AnswerViewSet._maybe_update_meta_sheets_for_feeder(puzzle)
            )

        return Response(PuzzleSerializer(puzzle).data)

    def partial_update(self, request, pk=None, **kwargs):
        puzzle = None
        with transaction.atomic():
            answer = self.get_object()
            old_answer = answer.text
            super().partial_update(request, pk, **kwargs)

            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])

            serializer = self.get_serializer(answer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            new_answer = data["text"]

            if old_answer == new_answer:
                return Response(PuzzleSerializer(puzzle).data)

            transaction.on_commit(
                lambda: AnswerViewSet._maybe_update_meta_sheets_for_feeder(puzzle)
            )

            if puzzle.chat_room:
                transaction.on_commit(
                    lambda: chat.tasks.handle_answer_change.delay(
                        puzzle.id, old_answer, new_answer
                    )
                )

            transaction.on_commit(
                lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
            )

        return Response(PuzzleSerializer(puzzle).data)


class PuzzleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PuzzleSerializer

    def get_queryset(self):
        hunt_id = self.kwargs["hunt_id"]
        return (
            Puzzle.objects.filter(hunt__id=hunt_id)
            .select_related("chat_room")
            .prefetch_related("metas", "feeders")
            .prefetch_related("tags")
            .prefetch_related(
                Prefetch(
                    "guesses",
                    queryset=Answer.objects.filter(status=Answer.CORRECT),
                    to_attr="_prefetched_correct_answers",
                )
            )
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
                old_name = puzzle.name
                serializer = self.get_serializer(
                    puzzle, data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                data = serializer.validated_data
                new_url = data.get("url", puzzle.url)
                url_changed = new_url != puzzle.url
                new_is_meta = data.get("is_meta", puzzle.is_meta)
                meta_status_changed = new_is_meta != puzzle.is_meta
                puzzle.update_metadata(
                    new_name=data.get("name", puzzle.name),
                    new_url=new_url,
                    new_is_meta=new_is_meta,
                )
                if "status" in data:
                    old_status = puzzle.status
                    puzzle.status = data["status"]
                    puzzle.save()
                    if puzzle.status == Puzzle.SOLVED:
                        if puzzle.chat_room:
                            # TODO: handle multiple answers here
                            transaction.on_commit(
                                lambda: chat.tasks.handle_puzzle_solved.delay(
                                    puzzle.id,
                                    puzzle.guesses.filter(status=Answer.CORRECT)
                                    .first()
                                    .text,
                                )
                            )
                            transaction.on_commit(
                                lambda: chat.tasks.cleanup_puzzle_channels.apply_async(
                                    args=(puzzle.id,),
                                    countdown=1800,  # clean up in 30 minutes
                                )
                            )
                        transaction.on_commit(
                            lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
                        )
                    elif old_status == Puzzle.SOLVED and puzzle.status != Puzzle.SOLVED:
                        if puzzle.chat_room:
                            transaction.on_commit(
                                lambda: chat.tasks.handle_puzzle_unsolved.delay(
                                    puzzle.id
                                )
                            )
                        transaction.on_commit(
                            lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
                        )

                if "name" in data and data["name"] != old_name:
                    if puzzle.chat_room:
                        puzzle.chat_room.name = data["name"]
                        puzzle.chat_room.save()
                        transaction.on_commit(
                            lambda: chat.tasks.handle_puzzle_rename.delay(
                                puzzle.id, old_name, data["name"]
                            )
                        )
                    transaction.on_commit(
                        lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
                    )

                if url_changed and google_api_lib.enabled():
                    transaction.on_commit(
                        lambda: google_api_lib.tasks.add_puzzle_link_to_sheet.delay(
                            new_url, puzzle.sheet
                        )
                    )
                if puzzle.is_meta and google_api_lib.enabled():
                    transaction.on_commit(
                        lambda: google_api_lib.tasks.update_meta_and_metameta_sheets_delayed(
                            puzzle
                        )
                    )

                if meta_status_changed and puzzle.chat_room:
                    transaction.on_commit(
                        lambda: chat.tasks.handle_puzzle_meta_change.delay(puzzle.id)
                    )

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

            if settings.CHAT_DEFAULT_SERVICE:
                chat_room = ChatRoom.objects.create(
                    service=settings.CHAT_DEFAULT_SERVICE, name=name
                )
                transaction.on_commit(
                    lambda: chat.tasks.create_chat_for_puzzle.delay(puzzle.id)
                )
            else:
                logger.warn("Chat room not created for puzzle %s" % name)
                chat_room = None

            puzzle = serializer.save(hunt=hunt, chat_room=chat_room)

            if google_api_lib.enabled():
                transaction.on_commit(
                    lambda: google_api_lib.tasks.create_google_sheets.delay(puzzle.id)
                )
            else:
                logger.warn("Sheet not created for puzzle %s" % name)

        return Response(PuzzleSerializer(puzzle).data)


class PuzzleTagViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PuzzleTagSerializer

    def get_queryset(self):
        puzzle_id = self.kwargs["puzzle_id"]
        return PuzzleTag.objects.filter(puzzles__id=puzzle_id)

    def destroy(self, request, pk=None, **kwargs):
        puzzle = None
        meta = None
        with transaction.atomic():
            tag = self.get_object()
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            if puzzle.name == tag.name and tag.is_meta:
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

            if puzzle.chat_room:
                transaction.on_commit(
                    lambda: chat.tasks.handle_tag_removed.delay(puzzle.id, tag.name)
                )

            if tag.name.upper() == PuzzleTag.BACKSOLVED.upper():
                transaction.on_commit(
                    lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
                )
        if meta:
            return Response(
                [PuzzleSerializer(puzzle).data, PuzzleSerializer(meta).data]
            )
        else:
            return Response([PuzzleSerializer(puzzle).data])

    def create(self, request, **kwargs):
        puzzle = None
        meta = None
        with transaction.atomic():
            puzzle = get_object_or_404(Puzzle, pk=self.kwargs["puzzle_id"])
            serializer = self.get_serializer(
                data=request.data, context={"hunt": puzzle.hunt}
            )
            serializer.is_valid(raise_exception=True)
            tag_name, tag_color = (
                serializer.validated_data["name"],
                serializer.validated_data["color"],
            )
            tag, _ = PuzzleTag.objects.get_or_create(
                name=tag_name,
                hunt=puzzle.hunt,
            )
            if tag.is_meta:
                meta = get_object_or_404(Puzzle, name=tag.name, hunt=puzzle.hunt)
                if is_ancestor(puzzle, meta):
                    return Response(
                        {
                            "detail": '"Unable to assign metapuzzle since doing so would introduce a meta-cycle."'
                        },
                        status=400,
                    )
                else:
                    # the post m2m hook will add tag
                    puzzle.metas.add(meta)
            else:
                PuzzleTag.objects.filter(name=tag_name, hunt=puzzle.hunt).update(
                    color=tag_color,
                )
                puzzle.tags.add(tag)
                if (
                    tag.name == PuzzleTag.HIGH_PRIORITY
                    or tag.name == PuzzleTag.LOW_PRIORITY
                ):
                    opposite_tag_name = (
                        PuzzleTag.LOW_PRIORITY
                        if tag.name == PuzzleTag.HIGH_PRIORITY
                        else PuzzleTag.HIGH_PRIORITY
                    )
                    # This should be 0 or 1 entries.
                    maybe_tag_to_remove = PuzzleTag.objects.filter(
                        name=opposite_tag_name, hunt=puzzle.hunt
                    )
                    if maybe_tag_to_remove:
                        puzzle.tags.remove(maybe_tag_to_remove[0])

            if puzzle.chat_room:
                transaction.on_commit(
                    lambda: chat.tasks.handle_tag_added.delay(puzzle.id, tag.name)
                )

            if tag.name.upper() == PuzzleTag.BACKSOLVED.upper():
                transaction.on_commit(
                    lambda: AnswerViewSet._maybe_update_sheets_title(puzzle)
                )

        if meta:
            return Response(
                [PuzzleSerializer(puzzle).data, PuzzleSerializer(meta).data]
            )
        else:
            return Response([PuzzleSerializer(puzzle).data])
