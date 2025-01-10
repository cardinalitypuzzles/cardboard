import React from "react";
import { useDispatch } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { editAnswer } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

import type { Dispatch } from "./store";
import type { AnswerId, PuzzleId } from "./types";
import { SafeButton, SafeForm, SafeModal } from "./types";

function EditAnswerModal({ puzzleId, answerId, text } : { puzzleId: PuzzleId, answerId: AnswerId, text: string }) {
  const [newAnswer, setNewAnswer] = React.useState(text);
  const dispatch = useDispatch<Dispatch>();
  const onSubmit = (e: ChangeEvent) => {
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
      <SafeModal.Header closeButton>
        <SafeModal.Title>Edit Answer</SafeModal.Title>
      </SafeModal.Header>
      <SafeForm onSubmit={onSubmit}>
        <SafeModal.Body>
          <SafeForm.Control
            required
            autoFocus
            placeholder="Answer"
            value={newAnswer}
            onChange={(e: ChangeEvent) => setNewAnswer(e.target.value)}
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

export default EditAnswerModal;
