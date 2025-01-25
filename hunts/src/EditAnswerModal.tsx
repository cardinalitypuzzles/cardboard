import React from "react";
import { Button, Form, Modal } from "react-bootstrap";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

import { useStore } from "./store";
import type { AnswerId, PuzzleId } from "./types";

function EditAnswerModal({
  puzzleId,
  answerId,
  text,
}: {
  puzzleId: PuzzleId;
  answerId: AnswerId;
  text: string;
}) {
  const [newAnswer, setNewAnswer] = React.useState(text);
  const { editAnswer } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);
  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    editAnswer(puzzleId, answerId, newAnswer).finally(hideModal);
    return false;
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Answer</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit} autoComplete="off">
        <Modal.Body>
          <Form.Control
            required
            autoFocus
            placeholder="Answer"
            value={newAnswer}
            onChange={(e: ChangeEvent) => setNewAnswer(e.target.value)}
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

export default EditAnswerModal;
