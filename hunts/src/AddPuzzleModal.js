import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { addPuzzle } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

function AddPuzzleModal({ huntId }) {
  const [name, setName] = React.useState("");
  const [url, setUrl] = React.useState("");
  const [isMeta, setIsMeta] = React.useState(false);
  const dispatch = useDispatch();
  const onSubmit = () => {
    dispatch(
      addPuzzle({
        huntId,
        name,
        url,
        is_meta: isMeta,
      })
    ).finally(() => {
      dispatch(hideModal());
    });
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Add Puzzle</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group controlId="addPuzzle.name">
            <Form.Label>Puzzle name</Form.Label>
            <Form.Control
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="addPuzzle.url">
            <Form.Label>Puzzle url</Form.Label>
            <Form.Control
              placeholder="https://www.example.com/"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </Form.Group>
          <Form.Check
            type="checkbox"
            label="Is meta"
            checked={isMeta}
            onChange={(e) => setIsMeta(e.target.checked)}
          />
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => dispatch(hideModal())}>
          Cancel
        </Button>
        <Button variant="primary" onClick={onSubmit}>
          Add
        </Button>
      </Modal.Footer>
    </>
  );
}

export default AddPuzzleModal;
