import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import { selectPuzzleById, deletePuzzle } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

function DeletePuzzleModal({ huntId, puzzleId, puzzleName }) {
  const dispatch = useDispatch();
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
