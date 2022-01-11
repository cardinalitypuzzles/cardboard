from cardboard.settings import TaskPriority
from celery import shared_task
import logging
from django.db import transaction
from datetime import datetime, timedelta


from puzzles.models import Puzzle

logger = logging.getLogger(__name__)


@shared_task(priority=TaskPriority.HIGH.value)
def create_chat_for_puzzle(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.create_channels()
        msg = f"{puzzle.name} has been unlocked!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"create_chat_for_puzzle failed with error: {e}")


@shared_task
def cleanup_puzzle_channels(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    # check that puzzle wasn't unsolved between when task was queued and now
    with transaction.atomic():
        solved_time = puzzle.solved_time()
        if solved_time is None:
            return

        now = datetime.now(tz=solved_time.tzinfo)
        logger.warn(now - solved_time)
        if now - solved_time < timedelta(minutes=30):
            try:
                puzzle.chat_room.delete_channels(check_if_used=True)
            except Exception as e:
                logger.warn(f"cleanup_puzzle_channels failed with error: {e}")


@shared_task
def handle_puzzle_solved(puzzle_id, answer_text):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.archive_channels()
        msg = f"{puzzle.name} has been solved with {answer_text}!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_puzzle_solved failed with error: {e}")


@shared_task
def handle_puzzle_unsolved(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.unarchive_channels()
        puzzle.chat_room.create_channels()
        msg = f"{puzzle.name} is no longer solved!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_puzzle_unsolved failed with error: {e}")


@shared_task
def handle_tag_added(puzzle_id, tag_name):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_tag_added(puzzle, tag_name)
    except Exception as e:
        logger.warn(f"handle_tag_added failed with error: {e}")


@shared_task
def handle_tag_removed(puzzle_id, tag_name):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_tag_removed(puzzle, tag_name)
    except Exception as e:
        logger.warn(f"handle_tag_removed failed with error: {e}")


@shared_task
def handle_answer_change(puzzle_id, old_answer, new_answer):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        msg = f"{puzzle.name}'s answer changed from {old_answer} to {new_answer}."
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_answer_change failed with error: {e}")


@shared_task
def handle_puzzle_rename(puzzle_id, old_name, new_name):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_puzzle_rename(new_name)
        msg = f"**{old_name}** has been renamed to **{new_name}**."
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"handle_puzzle_rename failed with error: {e}")


@shared_task
def handle_sheet_created(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        msg = "Sheet has been created!"
        puzzle.chat_room.send_message(msg, embedded_urls={"Sheet": puzzle.sheet})
    except Exception as e:
        logger.warn(f"handle_sheet_created failed with error: {e}")
