import React from "react";
import DropdownButton from "react-bootstrap/DropdownButton";
import Dropdown from "react-bootstrap/Dropdown";
import { useSelector, useDispatch } from "react-redux";
import { updatePuzzle } from "./puzzlesSlice";

export default function StatusCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  const statuses_to_display = ["SOLVING", "STUCK", "EXTRACTION"];
  if (value === "SOLVED") {
    statuses_to_display.push("SOLVED");
  }
  return (
    <>
      <DropdownButton
        id={`status-dropdown-${row.id}`}
        title={value}
        variant="outline-primary"
        onSelect={(status) => {
          dispatch(
            updatePuzzle({
              huntId,
              id: row.values.id,
              body: { status },
            })
          );
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
