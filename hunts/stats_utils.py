from django.db.models import Q

from .models import Hunt
from puzzles.models import Puzzle

def get_num_solved(hunt):
    return hunt.puzzles.filter(status=Puzzle.SOLVED).count()

def get_num_unsolved(hunt):
    return hunt.puzzles.filter(~Q(status=Puzzle.SOLVED)).count()

def get_num_unlocked_puzzles(hunt):
    return hunt.puzzles.count()

def get_num_metas_solved(hunt):
    return hunt.puzzles.filter(Q(status=Puzzle.SOLVED),Q(is_meta=True)).count()
