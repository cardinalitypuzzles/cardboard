import { IconUsers } from "@tabler/icons";
import React from "react";
import Popover from "react-bootstrap/Popover";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import { Badge } from "react-bootstrap";

import type { Puzzle, Row } from "./types";
import { SafeBadge, SafeOverlayTrigger, SafePopover } from "./types";

const getColor = (count: number) => {
  if (count <= 4) {
    return "text-success";
  } else if (count <= 8) {
    return "text-warning";
  } else {
    return "text-danger";
  }
};

export default ({ row } : { row: Row<Puzzle> }) => {
  const recentEditors = row.values.recentEditors;
  const topEditors = row.values.topEditors;
  if (recentEditors.length + topEditors.length > 0) {
    const editorsPopover = (
      <SafePopover className="bootstrap">
        {row.values.recentEditors.length > 0 && (
          <>
            <SafePopover.Title>Recent Editors</SafePopover.Title>
            <SafePopover.Content>
              {recentEditors.map((editor: string) => (
                <div key={editor}>{editor}</div>
              ))}
            </SafePopover.Content>
          </>
        )}
        {row.values.topEditors.length > 0 && (
          <>
            <SafePopover.Title>Top Editors</SafePopover.Title>
            <SafePopover.Content>
              {topEditors.map((editor: string) => (
                <div key={editor}>{editor}</div>
              ))}
            </SafePopover.Content>
          </>
        )}
      </SafePopover>
    );
    return (
      <SafeOverlayTrigger
        trigger={["hover", "focus"]}
        placement="right"
        overlay={editorsPopover}
      >
        <SafeBadge
          className={getColor(recentEditors.length)}
          style={{
            whiteSpace: "nowrap",
            fontSize: "100%",
          }}
          variant="light"
        >
          <IconUsers size={16} />
          {recentEditors.length}
        </SafeBadge>
      </SafeOverlayTrigger>
    );
  } else {
    return null;
  }
};
