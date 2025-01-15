import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { useDispatch } from "react-redux";
import { editNotes } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

import type { Dispatch } from "./store";
import type { PuzzleId } from "./types";

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
  const onSubmit = (e: FormEvent) => {
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
          <Button variant="secondary" onClick={() => dispatch(hideModal())}>
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
