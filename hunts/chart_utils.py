from django.utils import timezone

from .models import Hunt
from puzzles.models import Puzzle


def can_use_chart(hunt):
    if not hunt.start_time:
        if hunt.get_num_unlocked() == 0:
            return False
        else:
            return True

    if timezone.now() <= hunt.start_time:
        return False

    return True


# Returns a tuple of lists of solved puzzle data, all sorted in order of puzzle solve time.
# labels: Names of solved puzzles
# times: Solve times of solved puzzles, in ISO 8601 format strings
# counts: Cumulative count of solves at the time of that puzzle's solve (inclusive)
# is_meta: Whether the solved puzzle is meta (list of booleans)
def get_chart_data(hunt):

    # if start_time not given, use first puzzle creation time
    # (use can_use_chart() to check beforehand)
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

    queryset = hunt.puzzles.filter(status=Puzzle.SOLVED)
    solved_counts = queryset.count()
    sorted_puzzles = sorted(queryset, key=lambda x: x.solved_time())

    for i, puzzle in enumerate(sorted_puzzles):
        if puzzle.solved_time() > chart_end_time:
            solved_counts = i
            break
        labels.append(puzzle.name)
        times.append(puzzle.solved_time().isoformat())
        counts.append(i + 1)
        is_meta.append(puzzle.is_meta)

    if hunt.end_time and chart_end_time < hunt.end_time:
        labels.append("Now")
    else:
        labels.append("End")
    times.append(chart_end_time.isoformat())
    counts.append(solved_counts)
    is_meta.append(False)

    return (labels, times, counts, is_meta)
