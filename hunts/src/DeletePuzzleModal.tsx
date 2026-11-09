import React from "react";
import { Button, Modal } from "react-bootstrap";

import { useStore } from "./store";
import type { PuzzleId, HuntId } from "./types";

function DeletePuzzleModal({
  huntId,
  puzzleId,
  puzzleName,
}: {
  huntId: HuntId;
  puzzleId: PuzzleId;
  puzzleName: string;
}) {
  const { deletePuzzle } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);

  const onDelete = () => {
    deletePuzzle(puzzleId).finally(hideModal);
  };

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Delete {puzzleName}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        Are you sure you want to delete <b>{puzzleName}</b>?
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={hideModal}>
          Cancel
        </Button>
        <Button variant="danger" onClick={onDelete}>
          Delete
        </Button>
      </Modal.Footer>
    </>
  );
}

export default DeletePuzzleModal;
