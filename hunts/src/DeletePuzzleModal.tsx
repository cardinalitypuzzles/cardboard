import React from "react";
import { useDispatch } from "react-redux";
import { Button, Modal } from "react-bootstrap";
import { deletePuzzle } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

import type { Dispatch } from "./store";
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
  const dispatch = useDispatch<Dispatch>();
  const onDelete = () => {
    dispatch(deletePuzzle({ huntId, id: puzzleId })).finally(() => {
      dispatch(hideModal());
    });
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

export default DeletePuzzleModal;
