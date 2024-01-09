import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { addPuzzle } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";
import { selectHuntTags } from "./huntSlice";

function AddPuzzleModal({ huntId }) {
  const allTags = useSelector(selectHuntTags);
  const [name, setName] = React.useState("");
  const [url, setUrl] = React.useState("");
  const [assignedMeta, setAssignedMeta] = React.useState("");
  const [isMeta, setIsMeta] = React.useState(false);
  const [createChannels, setCreateChannels] = React.useState(true);
  const dispatch = useDispatch();
  const onSubmit = (e) => {
    e.preventDefault();
    dispatch(
      addPuzzle({
        huntId,
        name,
        url,
        is_meta: isMeta,
        create_channels: createChannels,
        assigned_meta: assignedMeta,
      })
    ).finally(() => {
      dispatch(hideModal());
    });
    return false;
  };

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Add Puzzle</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit}>
        <Modal.Body>
          <Form.Group controlId="addPuzzle.name">
            <Form.Label>Puzzle name</Form.Label>
            <Form.Control
              required
              placeholder="Name"
              value={name}
              autoFocus
              onChange={(e) => setName(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="addPuzzle.url">
            <Form.Label>Puzzle urls</Form.Label>
            <Form.Control
              required
              placeholder="https://www.example.com/"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="addPuzzle.meta">
            <Form.Label>Assigned Meta</Form.Label>
            <Form.Control
              as="select"
              value={assignedMeta}
              onChange={(e) => setAssignedMeta(e.target.value)}
            >
              <option key="none" value="">
                None
              </option>
              {allTags
                .filter((tag) => tag.is_meta)
                .map((tag, i) => (
                  <option key={tag.name} value={tag.name}>
                    {tag.name}
                  </option>
                ))}
            </Form.Control>
          </Form.Group>
          <Form.Check
            type="checkbox"
            label="Is meta?"
            id="is-meta-checkbox"
            checked={isMeta}
            onChange={(e) => setIsMeta(e.target.checked)}
          />
          <Form.Check
            type="checkbox"
            label="Create discord channels"
            id="create-channels-checkbox"
            checked={createChannels}
            onChange={(e) => setCreateChannels(e.target.checked)}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => dispatch(hideModal())}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Add
          </Button>
        </Modal.Footer>
      </Form>
    </>
  );
}

export default AddPuzzleModal;
