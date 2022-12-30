import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export default function ClickableIcon({ icon, onClick }) {
  return (
    <span
      style={{ cursor: "pointer" }}
      className="text-muted"
      onClick={onClick}
    >
      <FontAwesomeIcon icon={icon} />
    </span>
  );
}

export const IconLink = ({ icon, url, size, style }) => {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="text-muted"
      style={style}
    >
      <FontAwesomeIcon icon={icon} size={size} />
    </a>
  );
};
