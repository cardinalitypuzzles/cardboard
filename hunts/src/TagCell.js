import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { showModal } from "./modalSlice";
import { toggleFilterTag } from "./filterSlice";
import TagPill from "./TagPill";

function TagCell({ row }) {
  const dispatch = useDispatch();
  const { id: huntId } = useSelector((state) => state.hunt);
  const puzzleId = row.original.id;

  const shouldShowMetaTags =
    row.original.tags.filter((t) => t.is_meta).length > 1;
  const tagsToShow = shouldShowMetaTags
    ? row.original.tags
    : row.original.tags.filter((t) => !t.is_meta);

  return (
    <>
      {tagsToShow.map(({ name, color, id }) => (
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
