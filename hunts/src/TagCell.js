import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { showModal } from "./modalSlice";
import { toggleFilterTag } from "./filterSlice";
import TagPill from "./TagPill";
import ClickableIcon from "./ClickableIcon";

function TagCell({ row }) {
  const dispatch = useDispatch();
  const { id: huntId } = useSelector((state) => state.hunt);
  const puzzleId = row.original.id;
  return (
    <>
      {row.original.tags
        .filter((t) => !t.is_meta)
        .map(({ name, color, id }) => (
          <TagPill
            name={name}
            color={color}
            id={id}
            puzzleId={puzzleId}
            key={name}
            onClick={() => dispatch(toggleFilterTag({ name, color, id }))}
          />
        ))}{" "}
    </>
  );
}

export default TagCell;
