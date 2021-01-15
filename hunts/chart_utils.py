from django.db.models import Max, Case, When
from django.utils import timezone

from .models import Hunt
from puzzles.models import Puzzle


def can_use_chart(hunt):
    if not hunt.start_time:
        return hunt.get_num_unlocked() > 0

    return timezone.now() > hunt.start_time


# Returns a tuple of lists of solved puzzle data, sorted by puzzle solve time.
# labels: Names of solved puzzles
# times: Solve times of solved puzzles, in ISO 8601 format strings
# counts: Total solves/unlocks at the time of that puzzle's solve/unlock (inclusive)
# is_meta: Whether the solved puzzle is meta (list of booleans)
def get_chart_data(hunt, unlocks=False):
    if not can_use_chart(hunt):
        return None

    # if start_time not given, use first puzzle creation time
    chart_start_time = hunt.start_time
    if not chart_start_time:
        chart_start_time = hunt.puzzles.earliest("created_on").created_on

    labels = ["Start"]
    times = [chart_start_time.isoformat()]
    counts = [0]
    is_meta = [False]

    chart_end_time = timezone.now()
    if hunt.end_time:
        chart_end_time = min(chart_end_time, hunt.end_time)

    if unlocks:
        sorted_puzzles = hunt.puzzles.all().order_by("created_on")
    else:
        sorted_puzzles = (
            hunt.puzzles.filter(status=Puzzle.SOLVED)
            .annotate(
                _solved_time=Max(
                    Case(When(guesses__status="CORRECT", then="guesses__created_on"))
                )
            )
            .order_by("_solved_time")
        )
    total_count = sorted_puzzles.count()

    for i, puzzle in enumerate(sorted_puzzles):
        if (not unlocks and puzzle._solved_time > chart_end_time) or (
            unlocks and puzzle.created_on > chart_end_time
        ):
            total_count = i
            break
        labels.append(puzzle.name)
        if unlocks:
            time_data = puzzle.created_on
        else:
            time_data = puzzle._solved_time
        if time_data < chart_start_time:
            time_data = chart_start_time
        times.append(time_data.isoformat())
        counts.append(i + 1)
        if not unlocks:
            is_meta.append(puzzle.is_meta)

    if hunt.end_time and chart_end_time < hunt.end_time:
        labels.append("Now")
    else:
        labels.append("End")
    times.append(chart_end_time.isoformat())
    counts.append(total_count)
    is_meta.append(False)

    if unlocks:
        return (labels, times, counts)
    return (labels, times, counts, is_meta)
