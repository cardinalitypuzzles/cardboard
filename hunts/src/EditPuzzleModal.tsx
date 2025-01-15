import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";
import { selectPuzzleTags, updatePuzzle } from "./puzzlesSlice";
import { showModal, hideModal } from "./modalSlice";
import EditableTagList from "./EditableTagList";

import type { Dispatch } from "./store";
import type { HuntId, PuzzleId } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function EditPuzzleModal({
  huntId,
  puzzleId,
  name,
  url,
  isMeta,
  hasChannels,
}: {
  huntId: HuntId;
  puzzleId: PuzzleId;
  name: string;
  url: string;
  isMeta: boolean;
  hasChannels: boolean;
}) {
  const [newName, setNewName] = React.useState(name);
  const [newUrl, setNewUrl] = React.useState(url);
  const [newIsMeta, setNewIsMeta] = React.useState(isMeta);
  const [createChannels, setCreateChannels] = React.useState(hasChannels);
  const dispatch = useDispatch<Dispatch>();

  const tags = useSelector(selectPuzzleTags);

  const onSubmit = (e: FormEvent) => {
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
      dispatch(hideModal());
    });
    return false;
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Puzzle</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit} autoComplete="off">
        <Modal.Body>
          <Form.Group controlId="editPuzzle.name">
            <Form.Label>Puzzle name</Form.Label>
            <Form.Control
              required
              autoFocus
              placeholder="Name"
              value={newName}
              onChange={(e: ChangeEvent) => setNewName(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="editPuzzle.url">
            <Form.Label>Puzzle url</Form.Label>
            <Form.Control
              required
              placeholder="https://www.example.com/"
              value={newUrl}
              onChange={(e: ChangeEvent) => setNewUrl(e.target.value)}
            />
          </Form.Group>
          <Form.Check
            type="checkbox"
            label="Is meta"
            id="is-meta-checkbox"
            checked={newIsMeta}
            onChange={(e: ChangeEvent) => setNewIsMeta(e.target.checked)}
          />
          <h5 style={{ textAlign: "center" }}>Parent Metas</h5>
          <EditableTagList
            puzzleId={puzzleId}
            tags={tags.filter((tag) => tag.is_meta && tag.name != name)}
          />
          <Form.Check
            type="checkbox"
            label="Create discord channels"
            id="create-channels-checkbox"
            checked={createChannels}
            onChange={(e: ChangeEvent) => setCreateChannels(e.target.checked)}
            // If channel is already created, disable its deletion
            disabled={hasChannels}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="danger"
            onClick={() => {
              hideModal();
              dispatch(
                showModal({
                  type: "DELETE_PUZZLE",
                  props: {
                    huntId,
                    puzzleId: puzzleId,
                    puzzleName: name,
                  },
                })
              );
            }}
            className="me-auto"
          >
            Delete Puzzle
          </Button>
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
