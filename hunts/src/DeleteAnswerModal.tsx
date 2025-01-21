import React from "react";
import { Button, Modal } from "react-bootstrap";

import { useStore } from "./store";
import type { AnswerId, PuzzleId } from "./types";

function DeleteAnswerModal({
  puzzleId,
  answerId,
}: {
  puzzleId: PuzzleId;
  answerId: AnswerId;
}) {
  const { deleteAnswer } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);

  const onDelete = () => {
    deleteAnswer(puzzleId, answerId).finally(() => {
      hideModal();
    });
  };

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Delete Answer</Modal.Title>
      </Modal.Header>
      <Modal.Body>Are you sure you want to delete this answer?</Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => hideModal()}>
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
