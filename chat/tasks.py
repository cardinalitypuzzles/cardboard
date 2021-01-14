from django.conf import settings
from smallboard.settings import TaskPriority
from celery import shared_task
import logging

from puzzles.models import Puzzle
from chat.models import ChatRoom

logger = logging.getLogger(__name__)


@shared_task(priority=TaskPriority.HIGH.value)
def create_chat_for_puzzle(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.create_channels()
        msg = f"{puzzle.name} has been unlocked!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_puzzle_solved(puzzle_id, answer_text):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.archive_channels()
        msg = f"{puzzle.name} has been solved with {answer_text}!"
        puzzle.chat_room.send_and_announce_message(msg)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_puzzle_unsolved(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.unarchive_channels()
        msg = f"{puzzle.name} is no longer solved!"
        puzzle.chat_room.send_and_announce_message(msg)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_tag_added(puzzle_id, tag_name):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_tag_added(puzzle, tag_name)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_tag_removed(puzzle_id, tag_name):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_tag_removed(puzzle, tag_name)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_answer_change(puzzle_id, old_answer, new_answer):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        msg = f"{puzzle.name}'s answer changed from {old_answer} to {new_answer}."
        puzzle.chat_room.send_and_announce_message(msg)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_sheet_created(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        msg = "Sheet has been created!"
        puzzle.chat_room.send_message(msg, embedded_urls={"Sheet": puzzle.sheet})
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")
