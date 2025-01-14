import React from "react";
import { useDispatch } from "react-redux";
import { Button, Modal } from "react-bootstrap";
import { deleteAnswer } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

import type { Dispatch } from "./store";
import type { AnswerId, PuzzleId } from "./types";

function DeleteAnswerModal({
  puzzleId,
  answerId,
}: {
  puzzleId: PuzzleId;
  answerId: AnswerId;
}) {
  const dispatch = useDispatch<Dispatch>();
  const onDelete = () => {
    dispatch(deleteAnswer({ puzzleId, answerId })).finally(() => {
      dispatch(hideModal());
    });
  };

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Delete Answer</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        Are you sure you want to delete this answer?
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => dispatch(hideModal())}>
          Cancel
        </Button>
        <Button variant="danger" onClick={onDelete}>
          Delete
        </Button>
      </Modal.Footer>
    </>
  );
}

export default DeleteAnswerModal;
