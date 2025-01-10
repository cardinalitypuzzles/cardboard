import React from "react";
import Badge from "react-bootstrap/Badge";
import { useSelector, useDispatch } from "react-redux";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { deletePuzzleTag, fetchPuzzles } from "./puzzlesSlice";

interface TagPillProps {
  name: string;
  color: string;
  id: number;
  puzzleId: number;
  selected?: boolean;
  faded?: boolean;
  editable?: boolean;
  onClick?: (() => void) | null;
}

function TagPill(props: TagPillProps) {
  const {
    name,
    color,
    id,
    puzzleId,
    selected = false,
    faded = false,
    editable = true,
    onClick = null,
  } = props;

  const { id: huntId } = useSelector((state: any) => state.hunt); // TODO: safely type this
  const dispatch = useDispatch();
  const style: React.CSSProperties = { margin: "2px" };
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
    // Not experienced enough with TS to know for sure, but it claims <Badge>
    // is an invalid JSX component and cannot be used.
    // afaict it may have to do with incompatibilities with newer versions of
    // React and old versions of react-bootstrap --
    // see https://github.com/react-bootstrap/react-bootstrap/issues/6819

    // @ts-ignore
    <Badge
      pill
      variant={color}
      key={name}
      onClick={onClick || undefined}
      style={style}
    >
      {name}
    </Badge>
  );
}

export default TagPill;
