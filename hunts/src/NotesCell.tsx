import React from "react";
import { showModal } from "./modalSlice";
import { useSelector, useDispatch } from "react-redux";
import { faWrench, faTag } from "@fortawesome/free-solid-svg-icons";
import ClickableIcon from "./ClickableIcon";

import huntReducer from './huntSlice';

import type { RootState } from "./store";
import type { Hunt, Row } from "./types";

export default function NotesCell({ row, value } : { row : Row, value: string }) {
  const { id: huntId } = useSelector<RootState, Hunt>((state) => state.hunt);
  const [uiHovered, setUiHovered] = React.useState(false);
  const dispatch = useDispatch();

  return (
    <div
      onMouseEnter={() => {
        setUiHovered(true);
      }}
      onMouseLeave={() => {
        setUiHovered(false);
      }}
    >
      {value}
      <div
        style={{
          display: "inline-block",
          visibility: uiHovered ? "visible" : "hidden",
        }}
        onMouseEnter={() => {
          setUiHovered(true);
        }}
        onMouseLeave={() => {
          setUiHovered(false);
        }}
      >
        <ClickableIcon
          icon={faWrench}
          onClick={() =>
            dispatch(
              showModal({
                type: "EDIT_NOTES",
                props: {
                  huntId,
                  puzzleId: row.values.id,
                  text: row.values.notes,
                },
              })
            )
          }
        />
      </div>
    </div>
  );
}
