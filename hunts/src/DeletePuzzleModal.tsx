import React from "react";
import { useDispatch } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
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

  // react-bootstrap component typing has a bug on old versions --
  // see https://github.com/react-bootstrap/react-bootstrap/issues/6819
  const SafeModal = Modal as any;
  const SafeButton = Button as any;
  return (
    <>
      <SafeModal.Header closeButton>
        <SafeModal.Title>Delete {puzzleName}</SafeModal.Title>
      </SafeModal.Header>
      <SafeModal.Body>
        Are you sure you want to delete <b>{puzzleName}</b>?
      </SafeModal.Body>
      <SafeModal.Footer>
        <SafeButton variant="secondary" onClick={() => dispatch(hideModal())}>
          Cancel
        </SafeButton>
        <SafeButton variant="danger" onClick={onDelete}>
          Delete
        </SafeButton>
      </SafeModal.Footer>
    </>
  );
}

export default DeletePuzzleModal;
