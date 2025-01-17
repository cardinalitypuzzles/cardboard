import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { editNotes } from "./puzzlesSlice";

import type { Dispatch, RootState } from "./store";
import type { Hunt, Row } from "./types";

export default function NotesCell({ row, value }: { row: Row; value: string }) {
  const { id: huntId } = useSelector<RootState, Hunt>((state) => state.hunt);
  const [uiHovered, setUiHovered] = useState(false);
  const [ editing, setEditing ] = useState(false);
  const [ editedNotesValue, setEditedNotesValue ] = useState(value);
  const dispatch = useDispatch<Dispatch>();

  return (
    <div
    className="clickable-puzzle-cell"
    onMouseEnter={() => {
      setUiHovered(true);
    }}
    onMouseLeave={() => {
      setUiHovered(false);
    }}
    onClick={() => {
      if (!editing) {
        setEditing(true);
        setEditedNotesValue(value);
      }
    }}
    >
      {editing ?
      <div style={{ display: 'flex' }}>
        <textarea
          autoFocus
          value={editedNotesValue}
          style={{ minHeight: '70px' }}
          onChange={(e) => {
            setEditedNotesValue(e.target.value);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.shiftKey || e.metaKey)) {
              dispatch(
                editNotes({
                  puzzleId: row.values.id,
                  body: { text: editedNotesValue },
                })
              ).finally(() => {
                setEditing(false);
              });
            } else if (e.key == "Escape") {
              setEditedNotesValue("");
              setEditing(false);
            }
          }}
        />
        <div
          style={{ cursor: 'pointer' }}
          onClick={() => {
            dispatch(
              editNotes({
                puzzleId: row.values.id,
                body: { text: editedNotesValue },
              })
            ).finally(() => {
              setEditing(false);
            });
          }}
        >
        ✓
        </div>
      </div>
      : value }
      </div>
  );
}
