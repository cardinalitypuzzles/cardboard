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
    lines_with_titles = []
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
        if p.chat_room and p.chat_room.text_channel_url:
            line += f"([chat]({p.chat_room.text_channel_url}))"

        lines_with_titles.append((line_title, line))
    print(f"lines: {lines_with_titles}")
    lines_with_titles.sort()

    # Discord embeds have a limit of:
    #   * 6000 total characters per embed
    #   * 25 fields per embed
    #   * 1024 characters per field.value
    # See the full limits: https://discord.com/developers/docs/resources/channel#embed-limits
    embed = discord.Embed(title=title)
    field_count = 0
    for line_title, line in lines_with_titles:
        line_length = len(line_title) + len(line)
        if (line_length + len(embed)) >= 6000 or field_count >= 25:
            await message.channel.send(embed=embed)
            embed = discord.Embed(title=title)
            field_count = 0
        embed.add_field(name=line_title, value=line, inline=True)
        field_count += 1
    await message.channel.send(embed=embed)


async def send_help(message):
    print("Sending help message")
    embed = discord.Embed(title="Cardi-P", description="Ahoy mateys, puzzle bot here!")
    commands = ["!puzzles", "!puzzles solved", "!puzzles stuck"]
    embed.add_field(name="Commands", value=", ".join(f"`{c}`" for c in commands))
    await message.channel.send(embed=embed)


class Command(BaseCommand):
    help = "Starts a Discord chat bot for interacting with Cardboard."

    def handle(self, *args, **options):
        self.stdout.write("Starting Discord bot")
        client.run(settings.DISCORD_API_TOKEN)
