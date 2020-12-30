from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
import discord

from puzzles.models import Puzzle

client = discord.Client()


@client.event
async def on_ready():
    print(f'Logged in as "{client.user}"')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f'Received message "{message.content}"')
    if message.content.startswith("!puzzles"):
        subcommand = parse_subcommand(message.content) or "unsolved"
        await handle_subcommand(message, subcommand)


def parse_subcommand(message_content):
    tokens = message_content.split()
    return tokens[1] if len(tokens) > 1 else None


async def handle_subcommand(message, subcommand):
    handle = {
        "unsolved": send_puzzles_unsolved,
        "solved": send_puzzles_solved,
        "stuck": send_puzzles_stuck,
    }.get(subcommand)
    await handle(message)


async def send_puzzles_unsolved(message):
    puzzles = await sync_to_async(list)(
        Puzzle.objects.filter(Q(status=Puzzle.SOLVING) | Q(status=Puzzle.PENDING))
    )
    await send_puzzles(message, puzzles, "Unsolved puzzles:")


async def send_puzzles_solved(message):
    puzzles = await sync_to_async(list)(Puzzle.objects.filter(status=Puzzle.SOLVED))
    await send_puzzles(message, puzzles, "Solved puzzles:")


async def send_puzzles_stuck(message):
    puzzles = await sync_to_async(list)(
        Puzzle.objects.filter(Q(status=Puzzle.STUCK) | Q(status=Puzzle.EXTRACTION))
    )
    await send_puzzles(message, puzzles, "Stuck puzzles:")


async def send_puzzles(message, puzzles, first_line):
    print(f"Sending puzzles {puzzles}")
    lines = [first_line]
    for p in puzzles:
        lines.append(f"- {p.name}")
    await message.channel.send("\n".join(lines))


class Command(BaseCommand):
    help = "Starts a Discord chat bot for interacting with Smallboard."

    def handle(self, *args, **options):
        self.stdout.write("Starting Discord bot")
        client.run(settings.DISCORD_API_TOKEN)
