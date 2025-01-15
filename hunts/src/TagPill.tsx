import React from "react";
import { Badge } from "react-bootstrap";

interface TagPillProps {
  name: string;
  color: string;
  selected?: boolean;
  faded?: boolean;
  onClick?: (() => void) | null;
}

function TagPill(props: TagPillProps) {
  const {
    name,
    color,
    selected = false,
    faded = false,
    onClick = null,
  } = props;

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
    <Badge
      pill
      bg={color}
      text={color === "light" ? "black" : "white"}
      key={name}
      onClick={onClick || undefined}
      style={style}
    >
      {name}
    </Badge>
  );
}

export default TagPill;
