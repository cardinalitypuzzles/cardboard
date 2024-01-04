import React from "react";
import { useDispatch } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { updatePuzzle, fetchPuzzles } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";
import { fetchHunt } from "./huntSlice";

function EditPuzzleModal({ huntId, puzzleId, name, url, isMeta, hasChannels }) {
  const [newName, setNewName] = React.useState(name);
  const [newUrl, setNewUrl] = React.useState(url);
  const [newIsMeta, setNewIsMeta] = React.useState(isMeta);
  const [createChannels, setCreateChannels] = React.useState(hasChannels);
  const dispatch = useDispatch();
  const onSubmit = (e) => {
    e.preventDefault();
    dispatch(
      updatePuzzle({
        huntId,
        id: puzzleId,
        body: {
          name: newName,
          url: newUrl,
          is_meta: newIsMeta,
          create_channels: createChannels,
        },
      })
    ).finally(() => {
      // Used to update hunt tags.
      dispatch(fetchHunt(huntId));
      dispatch(fetchPuzzles(huntId));

      dispatch(hideModal());
    });
    return false;
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Puzzle</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit}>
        <Modal.Body>
          <Form.Group controlId="editPuzzle.name">
            <Form.Label>Puzzle name</Form.Label>
            <Form.Control
              required
              autoFocus
              placeholder="Name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="editPuzzle.url">
            <Form.Label>Puzzle url</Form.Label>
            <Form.Control
              required
              placeholder="https://www.example.com/"
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
            />
          </Form.Group>
          <Form.Check
            type="checkbox"
            label="Is meta"
            id="is-meta-checkbox"
            checked={newIsMeta}
            onChange={(e) => setNewIsMeta(e.target.checked)}
          />
          <Form.Check
            type="checkbox"
            label="Create discord channels"
            id="create-channels-checkbox"
            checked={createChannels}
            onChange={(e) => setCreateChannels(e.target.checked)}
            // If channel is already created, disable its deletion
            disabled={hasChannels}
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

export default EditPuzzleModal;
