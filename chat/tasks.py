from cardboard.settings import TaskPriority
from celery import shared_task
import logging
from django.db import transaction
from django.db.models import Prefetch
from datetime import datetime, timedelta

from puzzles.models import Puzzle
from answers.models import Answer


logger = logging.getLogger(__name__)


def _get_puzzles_queryset():
    return Puzzle.objects.select_related("chat_room").select_related("hunt__settings")


@shared_task(rate_limit="6/m", acks_late=True, priority=TaskPriority.HIGH.value)
def create_chat_for_puzzle(puzzle_id):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    try:
        puzzle.chat_room.create_channels()
        msg = f"**{puzzle.name}** has been unlocked!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"create_chat_for_puzzle failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def cleanup_puzzle_channels(puzzle_id):
    puzzle = (
        _get_puzzles_queryset()
        .prefetch_related(
            Prefetch(
                "guesses",
                queryset=Answer.objects.filter(status=Answer.CORRECT),
            )
        )
        .get(id=puzzle_id)
    )
    # check that puzzle wasn't unsolved between when task was queued and now
    with transaction.atomic():
        solved_time = puzzle.solved_time()
        if solved_time is None:
            return

        now = datetime.now(tz=solved_time.tzinfo)
        if now - solved_time > timedelta(minutes=30):
            try:
                puzzle.chat_room.delete_channels(check_if_used=True)
            except Exception as e:
                logger.warn(f"cleanup_puzzle_channels failed with error: {e}")


# Disco-py actually kills the process when it is rate limited instead of throwing an exception
# acks_late=True and CELERY_TASK_REJECT_ON_WORKER_LOST in settings requeues those tasks
# the rate limit makes it wait. This is indeed really jank.
# TODO(#565): replace this rate limiting with global discord API rate limit
@shared_task(rate_limit="6/m", acks_late=True, priority=TaskPriority.LOW.value)
def handle_puzzle_meta_change(puzzle_id):
    """
    handles when the set of a puzzle's metas has changed OR the puzzle itself has toggled its is_meta state.
    """
    puzzle = _get_puzzles_queryset().prefetch_related("metas").get(id=puzzle_id)
    try:
        puzzle.chat_room.update_category()
    except Exception as e:
        logger.warn(f"handle_puzzle_meta_change failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_puzzle_solved(puzzle_id, answer_text):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    try:
        puzzle.chat_room.archive_channels()
        msg = f"**{puzzle.name}** has been solved with `{answer_text}`!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_puzzle_solved failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_puzzle_unsolved(puzzle_id):
    puzzle = _get_puzzles_queryset().prefetch_related("metas").get(id=puzzle_id)
    try:
        puzzle.chat_room.unarchive_channels()
        puzzle.chat_room.create_channels()
        msg = f"**{puzzle.name}** is no longer solved!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_puzzle_unsolved failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_tag_added(puzzle_id, tag_name):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_tag_added(puzzle, tag_name)
    except Exception as e:
        logger.warn(f"handle_tag_added failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_tag_removed(puzzle_id, tag_name):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_tag_removed(puzzle, tag_name)
    except Exception as e:
        logger.warn(f"handle_tag_removed failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_answer_change(puzzle_id, old_answer, new_answer):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    try:
        msg = (
            f"**{puzzle.name}**'s answer changed from `{old_answer}` to `{new_answer}`."
        )
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_answer_change failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_puzzle_rename(puzzle_id, old_name, new_name):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_puzzle_rename(new_name)
        msg = f"**{old_name}** has been renamed to **{new_name}**."
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_puzzle_rename failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_sheet_created(puzzle_id):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    try:
        msg = "Sheet has been created!"
        puzzle.chat_room.send_message(msg, embedded_urls={"Sheet": puzzle.sheet})
    except Exception as e:
        logger.warn(f"handle_sheet_created failed with error: {e}")
