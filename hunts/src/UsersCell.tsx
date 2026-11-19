import { IconUsers } from "@tabler/icons";
import React from "react";
import Popover from "react-bootstrap/Popover";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import { Badge } from "react-bootstrap";
import { useTranslation } from "react-i18next";

import type { PuzzleRow } from "./types";

const getColor = (count: number) => {
  if (count <= 4) {
    return "text-success";
  } else if (count <= 8) {
    return "text-warning";
  } else {
    return "text-danger";
  }
};

export default ({ row }: { row: PuzzleRow }) => {
  const { t } = useTranslation();
  const recentEditors = row.original.recent_editors;
  const topEditors = row.original.top_editors;
  if (recentEditors.length + topEditors.length > 0) {
    const editorsPopover = (
      <Popover className="bootstrap">
        {recentEditors.length > 0 && (
          <>
            <Popover.Header>{t("recent-editors")}</Popover.Header>
            <Popover.Body>
              {recentEditors.map((editor: string) => (
                <div key={editor}>{editor}</div>
              ))}
            </Popover.Body>
          </>
        )}
        {topEditors.length > 0 && (
          <>
            <Popover.Header>{t("top-editors")}</Popover.Header>
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
