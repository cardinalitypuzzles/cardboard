import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";

import { useStore } from "./store";
import type { PuzzleId } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function EditNotesModal({
  puzzleId,
  text,
}: {
  puzzleId: PuzzleId;
  text: string;
}) {
  const { editNotes } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);

  const [newNotes, setNewNotes] = React.useState(text);
  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    editNotes(puzzleId, newNotes).finally(hideModal);
    return false;
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Notes</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit} autoComplete="off">
        <Modal.Body>
          <Form.Control
            required
            autoFocus
            placeholder="Notes"
            value={newNotes}
            onChange={(e: ChangeEvent) => setNewNotes(e.target.value)}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={hideModal}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Submit
          </Button>
        </Modal.Footer>
      </Form>
    </>
  );
}

export default EditNotesModal;
