import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { updatePuzzle } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

function EditPuzzleModal({ huntId, puzzleId, name, url, isMeta }) {
  const [newName, setNewName] = React.useState(name);
  const [newUrl, setNewUrl] = React.useState(url);
  const [newIsMeta, setNewIsMeta] = React.useState(isMeta);
  const dispatch = useDispatch();
  const onSubmit = () => {
    dispatch(
      updatePuzzle({
        huntId,
        id: puzzleId,
        body: { name: newName, url: newUrl, is_meta: newIsMeta },
      })
    ).finally(() => {
      dispatch(hideModal());
    });
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Puzzle</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group controlId="editPuzzle.name">
            <Form.Label>Puzzle name</Form.Label>
            <Form.Control
              placeholder="Name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="editPuzzle.url">
            <Form.Label>Puzzle url</Form.Label>
            <Form.Control
              placeholder="https://www.example.com/"
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
            />
          </Form.Group>
          <Form.Check
            type="checkbox"
            label="Is meta"
            checked={newIsMeta}
            onChange={(e) => setNewIsMeta(e.target.checked)}
          />
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => dispatch(hideModal())}>
          Cancel
        </Button>
        <Button variant="primary" onClick={onSubmit}>
          Submit
        </Button>
      </Modal.Footer>
    </>
  );
}

export default EditPuzzleModal;
