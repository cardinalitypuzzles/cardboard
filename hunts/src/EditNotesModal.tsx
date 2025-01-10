import React from "react";
import { useDispatch } from "react-redux";
import { editNotes } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

import type { Dispatch } from "./store";
import type { PuzzleId } from "./types";
import { SafeButton, SafeForm, SafeModal } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function EditNotesModal({
  puzzleId,
  text,
}: {
  puzzleId: PuzzleId;
  text: string;
}) {
  const [newNotes, setNewNotes] = React.useState(text);
  const dispatch = useDispatch<Dispatch>();
  const onSubmit = (e: ChangeEvent) => {
    e.preventDefault();
    dispatch(
      editNotes({
        puzzleId,
        body: { text: newNotes },
      })
    ).finally(() => {
      dispatch(hideModal());
    });
    return false;
  };
  return (
    <>
      <SafeModal.Header closeButton>
        <SafeModal.Title>Edit Notes</SafeModal.Title>
      </SafeModal.Header>
      <SafeForm onSubmit={onSubmit}>
        <SafeModal.Body>
          <SafeForm.Control
            required
            autoFocus
            placeholder="Notes"
            value={newNotes}
            onChange={(e: ChangeEvent) => setNewNotes(e.target.value)}
          />
        </SafeModal.Body>
        <SafeModal.Footer>
          <SafeButton variant="secondary" onClick={() => dispatch(hideModal())}>
            Cancel
          </SafeButton>
          <SafeButton variant="primary" type="submit">
            Submit
          </SafeButton>
        </SafeModal.Footer>
      </SafeForm>
    </>
  );
}

export default EditNotesModal;
