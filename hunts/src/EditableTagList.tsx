import React from "react";
import { SELECTABLE_TAG_COLORS } from "./constants";
import TagPill from "./TagPill";

import { useStore } from "./store";
import type { PuzzleId, PuzzleTag } from "./types";

function EditableTagList({
  puzzleId,
  tags,
}: {
  puzzleId: PuzzleId;
  tags: PuzzleTag[];
}) {
  const { addPuzzleTag, deletePuzzleTag } = useStore(
    (state) => state.puzzlesSlice
  );
  const puzzleTags = useStore((state) => state.puzzlesSlice.allPuzzleTags());
  const puzzleTagIds = new Set(puzzleTags.map((tag) => tag.id));

  const selectable_colors = SELECTABLE_TAG_COLORS.map((tag) => tag.color);

  /* Assumes that tags are given in the order they should be displayed and */
  /* breaks them up into rows, with the first row being of the non-selectable colors */
  /* and subsequent rows alternating between the selectable colors */
  const groupedTags = tags.reduce((result: PuzzleTag[][], item) => {
    if (result.length == 0) {
      result.push([item]);
    } else if (!selectable_colors.includes(item.color)) {
      result[result.length - 1].push(item);
    } else if (result[result.length - 1][0].color == item.color) {
      result[result.length - 1].push(item);
    } else {
      result.push([item]);
    }

    return result;
  }, []);

  return groupedTags.map((group) => (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      {group.map((tag) => (
        <TagPill
          {...tag}
          selected={puzzleTagIds.has(tag.id)}
          faded={!puzzleTagIds.has(tag.id)}
          key={tag.name}
          onClick={() => {
            if (puzzleTagIds.has(tag.id)) {
              deletePuzzleTag(puzzleId, tag.id);
            } else {
              addPuzzleTag(puzzleId, { name: tag.name, color: tag.color });
            }
          }}
        />
      ))}
    </div>
  ));
}

export default EditableTagList;
