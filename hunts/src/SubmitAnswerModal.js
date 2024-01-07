import React from "react";
import { useDispatch } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { addAnswer, addPuzzleTag } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

function SubmitAnswerModal({ puzzleId, puzzleName }) {
  const [newAnswer, setNewAnswer] = React.useState("");
  const [backsolved, setBacksolved] = React.useState(false);

  const dispatch = useDispatch();
  const onSubmit = (e) => {
    e.preventDefault();
    if (backsolved) {
      dispatch(
        addPuzzleTag({
          puzzleId,
          name: "Backsolved",
          color: "success",
        })
      )
    }
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
        <Modal.Title>Submit Answer for {puzzleName} </Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit}>
        <Modal.Body>
          <Form.Control
            required
            placeholder="Enter Answer"
            value={newAnswer}
            autoFocus
            onChange={(e) => setNewAnswer(e.target.value)}
          />
          <Form.Check
            type="checkbox"
            defaultChecked={false}
            label="backsolved"
            value={backsolved}
            onChange={(e) => {
              e.target.checked ? setBacksolved(true) : setBacksolved(false)
            }}
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
