import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { showModal } from "./modalSlice";
import { toggleFilterTag } from "./filterSlice";
import TagPill from "./TagPill";
import ClickableIcon from "./ClickableIcon";

function TagCell({ row, value }) {
  const dispatch = useDispatch();
  const { id: huntId } = useSelector((state) => state.hunt);
  const puzzleId = row.original.id;
  return (
    <>
      {row.original.tags.map(({ name, color, id }) => (
        <TagPill
          name={name}
          color={color}
          id={id}
          puzzleId={puzzleId}
          key={name}
          onClick={() => dispatch(toggleFilterTag({ name, color, id }))}
        />
      ))}{" "}
      <ClickableIcon
        icon={faPlus}
        onClick={() =>
          dispatch(
            showModal({
              type: "EDIT_TAGS",
              props: {
                huntId,
                puzzleId: row.values.id,
              },
            })
          )
        }
      />
    </>
  );
}

export default TagCell;
