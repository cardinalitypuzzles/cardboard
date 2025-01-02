import React from "react";
import { useDispatch } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { editNotes } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

function EditNotesModal({ puzzleId, text }) {
  const [newNotes, setNewNotes] = React.useState(text);
  const dispatch = useDispatch();
  const onSubmit = (e) => {
    e.preventDefault();
    dispatch(
      editNotes({
        puzzleId,
        body: { text: newNotes },
      })
    ).finally(() => {
      dispatch(hideModal());
    });
    return false;
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Notes</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit}>
        <Modal.Body>
          <Form.Control
            required
            autoFocus
            placeholder="Notes"
            value={newNotes}
            onChange={(e) => setNewNotes(e.target.value)}
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

export default EditNotesModal;
