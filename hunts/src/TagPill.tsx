import React from "react";
import { Badge } from "react-bootstrap";
import { FAVORITE_TAG_COLOR, SELECTED_TAG_BORDER_COLOR } from "./constants";
import { useStore } from "./store";
import { interpolateWithGray, isLightColor } from "./utils";

interface TagPillProps {
  name: string;
  color: string;
  selected?: boolean;
  faded?: boolean;
  isMeta?: boolean;
  ignoreFavorite?: boolean;
  noMargin?: boolean;
  onClick?: React.MouseEventHandler<HTMLElement>;
}

function TagPill(props: TagPillProps) {
  const {
    name,
    color,
    selected = false,
    faded = false,
    isMeta = false,
    ignoreFavorite = false,
    noMargin = false,
    onClick = null,
  } = props;

  const favoriteTagNames = useStore(
    (state) => state.favoriteTagsSlice.favoriteTagNames
  );
  const isFavorite =
    !isMeta &&
    !ignoreFavorite &&
    Boolean(name) &&
    favoriteTagNames.includes(name.trim().toLowerCase());

  const baseColor = isFavorite ? FAVORITE_TAG_COLOR : color;
  const effectiveColor = faded ? interpolateWithGray(baseColor) : baseColor;
  const useDarkText = isLightColor(effectiveColor);

  const style: React.CSSProperties = {
    margin: noMargin ? "0px" : "2px",
    backgroundColor: effectiveColor,
    color: useDarkText ? "#000000" : "#ffffff",
  };
  if (selected) {
    style.border = `2px solid ${SELECTED_TAG_BORDER_COLOR}`;
  } else if (faded) {
    style.border = "2px solid transparent";
  }
  if (onClick !== null) {
    style.cursor = "pointer";
  }

  return (
    <Badge
      pill
      bg=""
      text={useDarkText ? "black" : "white"}
      key={name}
      onClick={onClick || undefined}
      style={style}
    >
      {name}
    </Badge>
  );
}

export default TagPill;
