import { IconUsers } from "@tabler/icons";
import React from "react";
import Popover from "react-bootstrap/Popover";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import { Badge } from "react-bootstrap";

import type { Puzzle, Row } from "./types";

const getColor = (count: number) => {
  if (count <= 4) {
    return "text-success";
  } else if (count <= 8) {
    return "text-warning";
  } else {
    return "text-danger";
  }
};

export default ({ row }: { row: Row<Puzzle> }) => {
  const recentEditors = row.values.recentEditors;
  const topEditors = row.values.topEditors;
  if (recentEditors.length + topEditors.length > 0) {
    const editorsPopover = (
      <Popover className="bootstrap">
        {row.values.recentEditors.length > 0 && (
          <>
            <Popover.Header>Recent Editors</Popover.Header>
            <Popover.Body>
              {recentEditors.map((editor: string) => (
                <div key={editor}>{editor}</div>
              ))}
            </Popover.Body>
          </>
        )}
        {row.values.topEditors.length > 0 && (
          <>
            <Popover.Header>Top Editors</Popover.Header>
            <Popover.Body>
              {topEditors.map((editor: string) => (
                <div key={editor}>{editor}</div>
              ))}
            </Popover.Body>
          </>
        )}
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
          bg="light"
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
