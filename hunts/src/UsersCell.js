import { IconUsers } from "@tabler/icons";
import React from "react";
import Popover from "react-bootstrap/Popover";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";

const TEXT_COLOR_GRADIENT = [
  "text-secondary",
  "text-info",
  "text-primary",
  "text-success",
  "text-warning",
  "text-danger",
];

const getColor = (count) => {
  if (count > TEXT_COLOR_GRADIENT.length) {
    return "text-danger";
  }
  return TEXT_COLOR_GRADIENT[count - 1];
};

export default ({ row }) => {
  if (row.original.recent_editors && row.original.recent_editors.length) {
    const recentEditors = row.original.recent_editors;
    const recentEditorsPopover = (
      <Popover className="bootstrap">
        <Popover.Title>Current Editors</Popover.Title>
        <Popover.Content>
          {recentEditors.map((editor) => (
            <div key={editor}>{editor}</div>
          ))}
        </Popover.Content>
      </Popover>
    );
    return (
      <OverlayTrigger
        trigger={["click"]}
        placement="right"
        overlay={recentEditorsPopover}
      >
        <div
          className={getColor(recentEditors.length)}
          style={{
            whiteSpace: "nowrap",
          }}
        >
          <IconUsers size={16} />
          {recentEditors.length}
        </div>
      </OverlayTrigger>
    );
  } else {
    return null;
  }
};
