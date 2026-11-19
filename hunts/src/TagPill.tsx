import React from "react";
import { Badge } from "react-bootstrap";
import { isLightColor } from "./utils";

interface TagPillProps {
  name: string;
  color: string;
  faded?: boolean;
  onClick?: React.MouseEventHandler<HTMLElement>;
}

function TagPill(props: TagPillProps) {
  const { name, color, faded = false, onClick = null } = props;

  const effectiveColor = faded ? "#6c757d" : color;
  const useDarkText = isLightColor(effectiveColor);
  const textColor = faded ? "#dee2e6" : useDarkText ? "#000000" : "#ffffff";

  const style: React.CSSProperties = {
    margin: "2px",
    backgroundColor: effectiveColor,
    color: textColor,
  };
  if (onClick !== null) {
    style.cursor = "pointer";
  }

  return (
    <Badge pill bg="" key={name} onClick={onClick || undefined} style={style}>
      {name}
    </Badge>
  );
}

export default TagPill;
