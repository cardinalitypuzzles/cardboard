import React from "react";
import Badge from "react-bootstrap/Badge";
import { useDispatch, useSelector } from "react-redux";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { showModal } from "./modalSlice";
import TagPill from "./TagPill";

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
          onClick={function () {row.original.addOrRemoveFilterTag({ name, color, id })}}
        />
      ))}
      <span
        style={{ cursor: "pointer" }}
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
      >
        <Badge pill variant="light">
          <FontAwesomeIcon icon={faPlus} />
        </Badge>
      </span>
    </>
  );
}

export default TagCell;
