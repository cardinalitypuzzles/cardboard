import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { updatePuzzle } from "./puzzlesSlice";

import type { Hunt, Puzzle, Row } from "./types";
import { Dispatch, RootState } from "./store";
import { SafeDropdown, SafeDropdownButton } from "./types";

export default function StatusCell({
  row,
  value,
}: {
  row: Row<Puzzle>;
  value: string;
}) {
  const { id: huntId } = useSelector<RootState, Hunt>((state) => state.hunt);
  const dispatch = useDispatch<Dispatch>();
  const statuses_to_display = ["SOLVING", "STUCK", "EXTRACTION"];
  if (value === "SOLVED" || row.original.guesses?.length > 0) {
    statuses_to_display.push("SOLVED");
  }
  return (
    <>
      <SafeDropdownButton
        id={`status-dropdown-${row.id}`}
        title={value}
        variant="outline-primary"
        className="cb-btn-compact"
        onSelect={(status: string) => {
          dispatch(
            updatePuzzle({
              huntId: huntId!,
              id: row.values.id,
              body: { status },
            })
          );
        }}
      >
        {statuses_to_display.map((status_to_display) => (
          <SafeDropdown.Item
            eventKey={status_to_display}
            key={status_to_display}
          >
            {status_to_display}
          </SafeDropdown.Item>
        ))}
      </SafeDropdownButton>
    </>
  );
}
