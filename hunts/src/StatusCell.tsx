import React from "react";
import { Dropdown, DropdownButton } from "react-bootstrap";
import api from "./api";

import type { Hunt, Puzzle, Row } from "./types";
import { useStore, RootState } from "./store";

export default function StatusCell({
  row,
  value,
}: {
  row: Row<Puzzle>;
  value: string;
}) {
  const huntId = useStore((store) => store.huntSlice.hunt.id);
  const { updatePuzzle } = useStore((store) => store.puzzlesSlice);
  const statuses_to_display = ["SOLVING", "STUCK", "EXTRACTION"];
  if (value === "SOLVED" || row.original.guesses?.length > 0) {
    statuses_to_display.push("SOLVED");
  }
  return (
    <>
      <DropdownButton
        id={`status-dropdown-${row.id}`}
        title={value}
        variant="outline-primary"
        className="cb-btn-compact"
        onSelect={(status: string | null) => {
          api.updatePuzzle(huntId!, row.values.id, {
            status: status ?? undefined,
          });
        }}
      >
        {statuses_to_display.map((status_to_display) => (
          <Dropdown.Item eventKey={status_to_display} key={status_to_display}>
            {status_to_display}
          </Dropdown.Item>
        ))}
      </DropdownButton>
    </>
  );
}
