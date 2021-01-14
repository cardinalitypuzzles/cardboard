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
        puzzle.chat_room.get_service().announce(msg)
        puzzle.chat_room.send_message(msg)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_puzzle_solved(puzzle_id, answer_text):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.archive_channels()
        msg = f"{puzzle.name} has been solved with {answer_text}!"
        puzzle.chat_room.get_service().announce(msg)
        puzzle.chat_room.send_message(msg)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")


@shared_task
def handle_puzzle_unsolved(puzzle_id):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.unarchive_channels()
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
def handle_channel_rename(puzzle_id, new_name):
    puzzle = Puzzle.objects.get(id=puzzle_id)
    try:
        puzzle.chat_room.handle_channel_rename(puzzle, tag_name)
    except Exception as e:
        logger.warn(f"Chat operations failed with error: {e}")
