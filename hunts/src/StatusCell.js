import React from "react";
import DropdownButton from "react-bootstrap/DropdownButton";
import Dropdown from "react-bootstrap/Dropdown";
import { useSelector, useDispatch } from "react-redux";
import { updatePuzzle } from "./puzzlesSlice";

export default function StatusCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  if (["SOLVING", "STUCK", "EXTRACTION"].includes(value)) {
    return (
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
        <Dropdown.Item eventKey="SOLVING">SOLVING</Dropdown.Item>
        <Dropdown.Item eventKey="STUCK">STUCK</Dropdown.Item>
        <Dropdown.Item eventKey="EXTRACTION">EXTRACTION</Dropdown.Item>
      </DropdownButton>
    );
  } else {
    return value;
  }
}
