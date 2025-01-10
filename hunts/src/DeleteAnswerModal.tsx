import React from "react";
import { useDispatch } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import { deleteAnswer } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

import type { Dispatch } from './store';
import type { AnswerId, PuzzleId } from "./types";
import { SafeButton, SafeModal } from "./types";


function DeleteAnswerModal({ puzzleId, answerId } : { puzzleId: PuzzleId, answerId: AnswerId }) {
  const dispatch = useDispatch<Dispatch>();
  const onDelete = () => {
    dispatch(deleteAnswer({ puzzleId, answerId })).finally(() => {
      dispatch(hideModal());
    });
  };
  
  return (
    <>
      <SafeModal.Header closeButton>
        <SafeModal.Title>Delete Answer</SafeModal.Title>
      </SafeModal.Header>
      <SafeModal.Body>Are you sure you want to delete this answer?</SafeModal.Body>
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

export default DeleteAnswerModal;
