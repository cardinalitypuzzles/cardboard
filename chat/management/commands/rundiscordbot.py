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
    print(f'{message.channel}/{message.author}: "{message.content}"')
    if message.content.startswith("!puzzles"):
        subcommand = parse_subcommand(message.content) or "unsolved"
        await handle_subcommand(message, subcommand)


def parse_subcommand(message_content):
    tokens = message_content.split()
    return tokens[1] if len(tokens) > 1 else None


async def handle_subcommand(message, subcommand):
    # Dispatch corresponding message response or default to help text.
    handle = {
        "unsolved": send_puzzles_unsolved,
        "solved": send_puzzles_solved,
        "stuck": send_puzzles_stuck,
    }.get(subcommand, send_help)
    await handle(message)


async def send_puzzles_unsolved(message):
    puzzles = await sync_to_async(list)(
        Puzzle.objects.filter(
            Q(hunt=settings.BOT_ACTIVE_HUNT),
            Q(status=Puzzle.SOLVING) | Q(status=Puzzle.PENDING),
        ).select_related("chat_room")
    )
    await send_puzzles(message, puzzles, "Unsolved puzzles")


async def send_puzzles_solved(message):
    puzzles = await sync_to_async(list)(
        Puzzle.objects.filter(
            hunt=settings.BOT_ACTIVE_HUNT, status=Puzzle.SOLVED
        ).select_related("chat_room")
    )
    await send_puzzles(message, puzzles, "Solved puzzles")


async def send_puzzles_stuck(message):
    puzzles = await sync_to_async(list)(
        Puzzle.objects.filter(
            Q(hunt=settings.BOT_ACTIVE_HUNT),
            Q(status=Puzzle.STUCK) | Q(status=Puzzle.EXTRACTION),
        ).select_related("chat_room")
    )
    await send_puzzles(message, puzzles, "Stuck puzzles")


async def send_puzzles(message, puzzles, title):
    print(f"Sending puzzles {puzzles}")
    embed = discord.Embed(title=title)
    lines = []
    for p in puzzles:
        line_title = ""
        if p.is_solved():
            line_title += f"[{p.answer}] "
        line_title += p.name

        line = ""
        if p.url:
            line += f"[Puzzle]({p.url}) "
        if p.sheet:
            line += f"([sheet](https://smallboard.app/puzzles/s/{p.id}))"
        if p.chat_room:
            if p.chat_room.text_channel_url:
                line += f"([chat]({p.chat_room.text_channel_url}))"

        lines.append((line_title, line))
    print(f"lines: {lines}")
    lines.sort()
    field_count = 0
    for line in lines:
        line_length = sum([len(x) for x in line])
        if (line_length + len(embed)) >= 6000 or field_count >= 25:
            await message.channel.send(embed=embed)
            embed = discord.Embed(title=title)
            embed_length = len(title)
            field_count = 0
        embed.add_field(name=line[0], value=line[1], inline=False)
        field_count += 1
    await message.channel.send(embed=embed)


async def send_help(message):
    print("Sending help message")
    embed = discord.Embed(title="Cardi-P", description="Ahoy mateys, puzzle bot here!")
    commands = ["!puzzles", "!puzzles solved", "!puzzles stuck"]
    embed.add_field(name="Commands", value=", ".join(f"`{c}`" for c in commands))
    await message.channel.send(embed=embed)


class Command(BaseCommand):
    help = "Starts a Discord chat bot for interacting with Smallboard."

    def handle(self, *args, **options):
        self.stdout.write("Starting Discord bot")
        client.run(settings.DISCORD_API_TOKEN)
