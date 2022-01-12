import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { addAnswer } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

function SubmitAnswerModal({ puzzleId, puzzleName }) {
  const [newAnswer, setNewAnswer] = React.useState("");
  const dispatch = useDispatch();
  const onSubmit = (e) => {
    e.preventDefault();
    dispatch(
      addAnswer({
        puzzleId,
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
        <Modal.Title> Enter Correct Answer for {puzzleName} </Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit}>
          <Modal.Body>
          Enter answer after submitting to Mystery Hunt first.
          <Form.Control
            required
            placeholder="Enter Answer"
            value={newAnswer}
            autoFocus
            onChange={(e) => setNewAnswer(e.target.value)}
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

export default SubmitAnswerModal;
