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
