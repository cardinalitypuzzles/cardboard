import React from "react";
import Badge from "react-bootstrap/Badge";
import { useSelector, useDispatch } from "react-redux";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faTimes } from "@fortawesome/free-solid-svg-icons";
import { deletePuzzleTag, fetchPuzzles } from "./puzzlesSlice";

function TagCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const puzzleId = row.original.id;
  const dispatch = useDispatch();
  return (
    <>
      {row.original.tags.map(({ name, color, id }) => (
        <Badge pill variant={color} key={name}>
          {name}
          <span
            onClick={() =>
              dispatch(deletePuzzleTag({ huntId, puzzleId, tagId: id })).then(
                () => {
                  if (is_meta) {
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
        </Badge>
      ))}
      <span style={{ cursor: "pointer" }}>
        <Badge pill variant="light">
          <FontAwesomeIcon icon={faPlus} />
        </Badge>
      </span>
    </>
  );
}

export default TagCell;
