import React from "react";
import { showModal } from "./modalSlice";
import { useSelector, useDispatch } from "react-redux";
import { faWrench, faTag } from "@fortawesome/free-solid-svg-icons";
import ClickableIcon from "./ClickableIcon";

export default function NotesCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
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
