import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { editNotes } from "./puzzlesSlice";

import type { Dispatch } from "./store";
import type { Row } from "./types";

export default function NotesCell({ row, value }: { row: Row; value: string }) {
  const [editing, setEditing] = useState(false);
  const [editedNotesValue, setEditedNotesValue] = useState(value);
  const dispatch = useDispatch<Dispatch>();

  return (
    <div
      className={!editing ? "clickable-puzzle-cell" : ""}
      onClick={() => {
        if (!editing) {
          setEditing(true);
          setEditedNotesValue(value);
        }
      }}
    >
      {editing ? (
        <div style={{ display: "flex" }}>
          <textarea
            autoFocus
            value={editedNotesValue}
            style={{ minHeight: "70px", width: "100%" }}
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
            style={{ cursor: "pointer" }}
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
      ) : (
        value
      )}
    </div>
  );
}
