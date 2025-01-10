import React from "react";

import { SafeFontAwesomeIcon } from "./types";

export default function ClickableIcon({
  icon,
  onClick,
}: {
  icon: any;
  onClick: () => void;
}) {
  return (
    <span
      style={{ cursor: "pointer" }}
      className="text-muted"
      onClick={onClick}
    >
      <SafeFontAwesomeIcon icon={icon} />
    </span>
  );
}

export const IconLink = ({
  icon,
  url,
  size,
  style,
}: {
  icon: any;
  url: string;
  size?: string;
  style?: React.CSSProperties;
}) => {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="text-muted"
      style={style}
    >
      <SafeFontAwesomeIcon icon={icon} size={size} />
    </a>
  );
};
