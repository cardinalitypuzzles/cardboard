import React, { useState } from "react";

import { useStore } from "./store";
import type { Row } from "./types";

export default function NotesCell({ row, value }: { row: Row; value: string }) {
  const [editing, setEditing] = useState(false);
  const [editedNotesValue, setEditedNotesValue] = useState(value);
  const { updatePuzzle } = useStore((store) => store.puzzlesSlice);

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
                updatePuzzle(row.values.id, {
                  notes: editedNotesValue,
                }).finally(() => {
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
              updatePuzzle(row.values.id, { notes: editedNotesValue }).finally(
                () => {
                  setEditing(false);
                }
              );
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
