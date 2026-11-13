import React from "react";
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
  const puzzles = useStore((state) => state.puzzlesSlice);
  const puzzleTagIds = new Set(
    puzzles.getPuzzle(puzzleId).tags.map((tag) => tag.id)
  );

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      {tags.map((tag) => (
        <TagPill
          name={tag.name}
          color={tag.color}
          isMeta={tag.is_meta}
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
  );
}

export default EditableTagList;
