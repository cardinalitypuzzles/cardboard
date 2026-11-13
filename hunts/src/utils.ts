import { SPECIAL_TAG_ORDER } from "./constants";
import { Puzzle, PuzzleTag } from "./types";

export function isLightColor(color: string): boolean {
  const hex = color.replace(/^#/, "");
  if (hex.length !== 6) {
    return false;
  }
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  if (Number.isNaN(r) || Number.isNaN(g) || Number.isNaN(b)) {
    return false;
  }
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness >= 140;
}

export function interpolateWithGray(color: string, grayRatio = 0.72): string {
  const hex = color.replace(/^#/, "");
  if (hex.length !== 6) {
    return "#6c757d";
  }
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  if (Number.isNaN(r) || Number.isNaN(g) || Number.isNaN(b)) {
    return "#6c757d";
  }
  const grayR = 108;
  const grayG = 117;
  const grayB = 125;
  const mix = (c: number, target: number) =>
    Math.round(c * (1 - grayRatio) + target * grayRatio)
      .toString(16)
      .padStart(2, "0");
  return `#${mix(r, grayR)}${mix(g, grayG)}${mix(b, grayB)}`;
}

export function sortPuzzleTags(tags: PuzzleTag[]): PuzzleTag[] {
  const priorityMap = new Map(
    SPECIAL_TAG_ORDER.map((name, idx) => [name.toLowerCase(), idx])
  );
  return [...tags].sort((a, b) => {
    const aRank = priorityMap.get(a.name.toLowerCase());
    const bRank = priorityMap.get(b.name.toLowerCase());
    if (aRank !== undefined && bRank !== undefined) {
      return aRank - bRank;
    }
    if (aRank !== undefined) {
      return -1;
    }
    if (bRank !== undefined) {
      return 1;
    }
    return a.id - b.id;
  });
}

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
