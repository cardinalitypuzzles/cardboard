import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import Prefetch

from answers.models import Answer
from cardboard.settings import TaskPriority
from hunts.models import Hunt
from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag, PuzzleTagColor

logger = logging.getLogger(__name__)


def _get_puzzles_queryset(include_deleted=False):
    if include_deleted:
        manager = Puzzle.global_objects
    else:
        manager = Puzzle.objects

    return manager.select_related("chat_room").select_related("hunt__settings")


@shared_task(rate_limit="6/m", acks_late=True, priority=TaskPriority.HIGH.value)
def announce_puzzle_unlock(puzzle_id):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        msg = f"**{puzzle.name}** has been unlocked!"
        puzzle.chat_room.announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.exception(f"announce_puzzle_unlock failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True, priority=TaskPriority.HIGH.value)
def create_channels_for_puzzle(puzzle_id):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        puzzle.chat_room.create_channels()
        msg = f"**{puzzle.name}** has been created!"
        puzzle.chat_room.send_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.exception(f"create_channels_for_puzzle failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def cleanup_puzzle_channels(puzzle_id):
    puzzle = (
        _get_puzzles_queryset(include_deleted=True)
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
        if solved_time is None and not puzzle.is_deleted:
            return

        puzzle.chat_room.delete_channels(check_if_used=True)


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
    if not puzzle.chat_room:
        return
    try:
        puzzle.chat_room.update_category()
    except Exception as e:
        logger.exception(f"handle_puzzle_meta_change failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_puzzle_solved(puzzle_id, answer_text):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        puzzle.chat_room.archive_channels()
        msg = f"**{puzzle.name}** has been solved with `{answer_text}`!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.exception(f"handle_puzzle_solved failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_puzzle_unsolved(puzzle_id):
    puzzle = _get_puzzles_queryset().prefetch_related("metas").get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        puzzle.chat_room.unarchive_channels()
        puzzle.chat_room.create_channels()
        msg = f"**{puzzle.name}** is no longer solved!"
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.exception(f"handle_puzzle_unsolved failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_tag_added(puzzle_id, tag_name):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        puzzle.chat_room.handle_tag_added(puzzle, tag_name)
    except Exception as e:
        logger.exception(f"handle_tag_added failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_tag_removed(puzzle_id, tag_name):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        puzzle.chat_room.handle_tag_removed(puzzle, tag_name)
    except Exception as e:
        logger.exception(f"handle_tag_removed failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_answer_change(puzzle_id, old_answer, new_answer):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        msg = (
            f"**{puzzle.name}**'s answer changed from `{old_answer}` to `{new_answer}`."
        )
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.exception(f"handle_answer_change failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_puzzle_rename(puzzle_id, old_name, new_name):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        puzzle.chat_room.handle_puzzle_rename(new_name)
        msg = f"**{old_name}** has been renamed to **{new_name}**."
        puzzle.chat_room.send_and_announce_message_with_embedded_urls(msg, puzzle)
    except Exception as e:
        logger.exception(f"handle_puzzle_rename failed with error: {e}")


@shared_task(rate_limit="6/m", acks_late=True)
def handle_sheet_created(puzzle_id):
    puzzle = _get_puzzles_queryset().get(id=puzzle_id)
    if not puzzle.chat_room:
        return
    try:
        msg = "Sheet has been created!"
        puzzle.chat_room.send_message(msg, embedded_urls={"Sheet": puzzle.sheet})
    except Exception as e:
        logger.exception(f"handle_sheet_created failed with error: {e}")


DISCORD_ROLE_COLOR_BLUE = 0x3498DB
DISCORD_ROLE_COLOR_WHITE = 0xFFFFFF


@shared_task(rate_limit="6/m", acks_late=True)
def sync_roles(hunt_slug, service_name):
    from django.conf import settings

    from chat.models import ChatRole

    hunt = Hunt.get_object_or_404(slug=hunt_slug)

    chat_service = settings.CHAT_SERVICES[service_name].get_instance()
    guild_id = hunt.settings.discord_guild_id

    discord_roles_by_name = {r["name"]: r for r in chat_service.get_all_roles(guild_id)}

    cardboard_tags = PuzzleTag.objects.filter(hunt=hunt)
    existing_chat_roles = ChatRole.objects.filter(hunt=hunt)

    default_tag_names = [n[0] for n in PuzzleTag.DEFAULT_TAGS]

    for tag in cardboard_tags:
        if (
            tag.color != PuzzleTagColor.BLUE and tag.color != PuzzleTagColor.WHITE
        ) or tag.name not in default_tag_names:
            continue

        # Create corresponding Discord tag, if needed
        if tag.name not in discord_roles_by_name:
            discord_tag_color = (
                DISCORD_ROLE_COLOR_BLUE
                if tag.color == PuzzleTagColor.BLUE
                else DISCORD_ROLE_COLOR_WHITE
            )
            new_role_info = chat_service.create_role(
                guild_id, tag.name, discord_tag_color
            )
            discord_roles_by_name[tag.name] = new_role_info
            logger.info(f"Created new Discord role {tag.name}")

        # Copy tag info into a ChatRole
        existing_chat_role = existing_chat_roles.filter(name=tag.name)
        if existing_chat_role.exists():
            obj = existing_chat_role.first()
            if obj.role_id != discord_roles_by_name[tag.name]["id"]:
                obj.role_id = discord_roles_by_name[tag.name]["id"]
                obj.save()
        else:
            obj = ChatRole(
                hunt=hunt,
                name=tag.name,
                role_id=discord_roles_by_name[tag.name]["id"],
            )
            obj.save()
