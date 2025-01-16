import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { showModal } from "./modalSlice";
import { faTag } from "@fortawesome/free-solid-svg-icons";
import { toggleFilterTag } from "./filterSlice";
import TagPill from "./TagPill";
import ClickableIcon from "./ClickableIcon";

import type { RootState } from "./store";
import type { Hunt, Puzzle, Row } from "./types";

function TagCell({ row }: { row: Row<Puzzle> }) {
  const [uiHovered, setUiHovered] = React.useState(false);
  const dispatch = useDispatch();
  const { id: huntId } = useSelector<RootState, Hunt>((state) => state.hunt);
  const puzzleId = row.original.id;

  const shouldShowMetaTags =
    row.original.tags.filter((t) => t.is_meta).length > 1;
  const tagsToShow = shouldShowMetaTags
    ? row.original.tags.filter(t => t.name !== row.original.name)
    : row.original.tags.filter((t) => !t.is_meta && t.name !== row.original.name);

  return (
    <div
     onMouseEnter={() => {
       setUiHovered(true);
     }}
     onMouseLeave={() => {
       setUiHovered(false);
     }}
     onClick={() => {
       dispatch(
        showModal({
          type: "EDIT_TAGS",
          props: {
            huntId,
            puzzleId: row.values.id,
            puzzleName: row.values.name,
          },
        })
       );
     }}
     style={{
       // TODO: abstract these properties out into their own CSS class
       cursor: 'pointer',
       minHeight: '1.4rem',
       backgroundColor: uiHovered ? '#ffe579' : undefined
     }}>
      {tagsToShow.map(({ name, color, id }) => (
        <TagPill
        name={name}
        color={color}
        key={name}
        onClick={() => dispatch(toggleFilterTag({ name, color, id }))}
        />
      ))}
    </div>
  );
}

export default TagCell;
