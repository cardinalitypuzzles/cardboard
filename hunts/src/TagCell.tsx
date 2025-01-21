import React from "react";
import { useStore } from "./store";
import TagPill from "./TagPill";

import type { RootState } from "./store";
import type { Hunt, Puzzle, Row } from "./types";

function TagCell({ row }: { row: Row<Puzzle> }) {
  const { modalSlice, hunt } = useStore((state) => ({
    modalSlice: state.modalSlice,
    hunt: state.huntSlice.hunt,
  }));
  const { toggleFilterTag } = useStore((state: RootState) => state.filterSlice);

  const shouldShowMetaTags =
    row.original.tags.filter((t) => t.is_meta).length > 1;
  const tagsToShow = shouldShowMetaTags
    ? row.original.tags.filter((t) => t.name !== row.original.name)
    : row.original.tags.filter(
        (t) => !t.is_meta && t.name !== row.original.name
      );

  return (
    <div
      className="clickable-puzzle-cell"
      onClick={() => {
        modalSlice.showModal({
          type: "EDIT_TAGS",
          props: {
            huntId: hunt.id,
            puzzleId: row.values.id,
            puzzleName: row.values.name,
          },
        });
      }}
    >
      {tagsToShow.map((tag) => (
        <TagPill
          name={tag.name}
          color={tag.color}
          key={tag.name}
          onClick={(e: React.MouseEvent) => {
            e.stopPropagation();
            toggleFilterTag(tag);
          }}
        />
      ))}
    </div>
  );
}

export default TagCell;
