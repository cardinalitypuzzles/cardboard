import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";

import { useStore } from "./store";
import type { PuzzleId } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function SubmitAnswerModal({
  puzzleId,
  puzzleName,
}: {
  puzzleId: PuzzleId;
  puzzleName: string;
}) {
  const { addAnswer, addPuzzleTag } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);

  const [newAnswer, setNewAnswer] = React.useState("");
  const [backsolved, setBacksolved] = React.useState(false);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (backsolved) {
      addPuzzleTag(puzzleId, {
        name: "Backsolved",
        color: "success",
      });
    }
    addAnswer(puzzleId, newAnswer).finally(hideModal);
    return false;
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Submit Answer for {puzzleName} </Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit} autoComplete="off">
        <Modal.Body>
          <Form.Control
            required
            placeholder="Enter Answer"
            value={newAnswer}
            autoFocus
            onChange={(e: ChangeEvent) => setNewAnswer(e.target.value)}
          />
          <Form.Check
            type="checkbox"
            defaultChecked={false}
            label="backsolved"
            value={backsolved.toString()}
            onChange={(e: ChangeEvent) => {
              e.target.checked ? setBacksolved(true) : setBacksolved(false);
            }}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={hideModal}>
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
