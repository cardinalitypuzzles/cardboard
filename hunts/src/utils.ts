import { Puzzle } from "./types";

export function puzzleComparator(a: Puzzle, b: Puzzle) {
  // Solved puzzles should appear below unsolved ones
  if (a.status == "SOLVED" && b.status != "SOLVED") {
    return 1;
  } else if (b.status == "SOLVED" && a.status != "SOLVED") {
    return -1;
  }
  // Feeders before metas
  if (!a.is_meta && b.is_meta) {
    return -1;
  } else if (a.is_meta && !b.is_meta) {
    return 1;
  }
  // High-priority before untagged before low-priority
  function priority(puzzle: Puzzle) {
    if (puzzle.tags.some((x) => x.is_high_pri)) {
      return 1;
    } else if (puzzle.tags.some((x) => x.is_low_pri)) {
      return -1;
    }
    return 0;
  }
  if (priority(b) != priority(a)) {
    return priority(b) - priority(a);
  }
  // Newer puzzles before old ones
  return Date.parse(b.created_on) - Date.parse(a.created_on);
}
