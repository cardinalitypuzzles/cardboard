import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import { deleteAnswer } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

function DeleteAnswerModal({ huntId, puzzleId, answerId }) {
  const dispatch = useDispatch();
  const onDelete = () => {
    dispatch(deleteAnswer({ huntId, puzzleId, answerId })).finally(() => {
      dispatch(hideModal());
    });
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Delete Answer</Modal.Title>
      </Modal.Header>
      <Modal.Body>Are you sure you want to delete this answer?</Modal.Body>
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
