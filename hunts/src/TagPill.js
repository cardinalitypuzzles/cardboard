import React from "react";
import Badge from "react-bootstrap/Badge";
import { useSelector, useDispatch } from "react-redux";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { deletePuzzleTag, fetchPuzzles } from "./puzzlesSlice";

function TagPill({
  name,
  color,
  id,
  puzzleId,
  editable = true,
  onClick = null,
}) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  const style = {};
  if (onClick !== null) {
    style.cursor = "pointer";
  }
  return (
    <Badge pill variant={color} key={name} onClick={onClick} style={style}>
      {name}
      {editable ? (
        <span
          onClick={() =>
            dispatch(deletePuzzleTag({ huntId, puzzleId, tagId: id })).then(
              (action) => {
                if (action.payload && action.payload.is_meta) {
                  // Deleting meta tags may affect the state of other puzzles
                  // (specifically their feeders)
                  // So just trigger a full fetch here.
                  // Alternatively we could try to duplicate the logic on the client
                  dispatch(fetchPuzzles(huntId));
                }
              }
            )
          }
          style={{ marginLeft: "5px", cursor: "pointer" }}
        >
          <FontAwesomeIcon icon={faTimes} />
        </span>
      ) : null}
    </Badge>
  );
}

export default TagPill;
