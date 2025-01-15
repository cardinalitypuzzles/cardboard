import React from "react";
import { useDispatch } from "react-redux";
import { Button, Form, Modal } from "react-bootstrap";
import { editAnswer } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

import type { Dispatch } from "./store";
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
  const dispatch = useDispatch<Dispatch>();
  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(
      editAnswer({
        puzzleId,
        answerId,
        body: { text: newAnswer },
      })
    ).finally(() => {
      dispatch(hideModal());
    });
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

export default EditAnswerModal;
