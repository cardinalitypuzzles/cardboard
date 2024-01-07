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
  selected = false,
  faded = false,
  editable = true,
  onClick = null,
}) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  const style = { margin: "2px" };
  if (onClick !== null) {
    style.cursor = "pointer";
  }
  if (selected) {
    style.border = "2px solid #5BC0DE";
    style.boxShadow = "0 0 2px #5BC0DE";
  }
  if (faded) {
    style.opacity = 0.5;
  }
  return (
    <Badge pill variant={color} key={name} onClick={onClick} style={style}>
      {name}
    </Badge>
  );
}

export default TagPill;
