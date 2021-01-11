from django.utils import timezone

from .models import Hunt
from puzzles.models import Puzzle


def can_use_chart(hunt):
    if not hunt.start_time or timezone.now() <= hunt.start_time:
        return False
    return True


def get_chart_data(hunt):
    labels = ["Start"]
    times = [hunt.start_time.isoformat()]
    counts = [0]
    is_meta = [False]

    current_time = timezone.now()
    if hunt.end_time:
        current_time = min(current_time, hunt.end_time)

    queryset = hunt.puzzles.filter(status=Puzzle.SOLVED)
    solved_counts = queryset.count()
    sorted_puzzles = sorted(queryset, key=lambda x: x.solved_time())

    for i, puzzle in enumerate(sorted_puzzles):
        if puzzle.solved_time() > current_time:
            solved_counts = i
            break
        labels.append(puzzle.name)
        times.append(puzzle.solved_time().isoformat())
        counts.append(i + 1)
        is_meta.append(puzzle.is_meta)

    labels.append("Now")
    times.append(current_time.isoformat())
    counts.append(solved_counts)
    is_meta.append(False)

    return (labels, times, counts, is_meta)
