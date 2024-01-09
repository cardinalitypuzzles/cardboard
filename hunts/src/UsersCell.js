import { IconUsers } from "@tabler/icons";
import React from "react";
import Popover from "react-bootstrap/Popover";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import { Badge } from "react-bootstrap";

const getColor = (count) => {
  if (count <= 4) {
    return "text-success";
  } else if (count <= 8) {
    return "text-warning";
  } else {
    return "text-danger";
  }
};

export default ({ row }) => {
  const recentEditors = row.values.recentEditors;
  const topEditors = row.values.topEditors;
  if (recentEditors.length + topEditors.length > 0) {
    const editorsPopover = (
      <Popover className="bootstrap">
        {row.values.recentEditors.length > 0 && (
          <>
            <Popover.Title>Recent Editors</Popover.Title>
            <Popover.Content>
              {recentEditors.map((editor) => (
                <div key={editor}>{editor}</div>
              ))}
            </Popover.Content>
          </>
        )}
        <Popover.Title>Top Editors</Popover.Title>
        <Popover.Content>
          {topEditors.map((editor) => (
            <div key={editor}>{editor}</div>
          ))}
        </Popover.Content>
      </Popover>
    );
    return (
      <OverlayTrigger
        trigger={["hover", "focus"]}
        placement="right"
        overlay={editorsPopover}
      >
        <Badge
          className={getColor(recentEditors.length)}
          style={{
            whiteSpace: "nowrap",
            fontSize: "100%",
          }}
          variant="light"
        >
          <IconUsers size={16} />
          {recentEditors.length}
        </Badge>
      </OverlayTrigger>
    );
  } else {
    return null;
  }
};
