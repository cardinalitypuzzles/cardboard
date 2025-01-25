import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import EditableTagList from "./EditableTagList";
import api from "./api";

import { useStore } from "./store";
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

  const { showModal, hideModal } = useStore((state) => state.modalSlice);

  const tags = useStore((state) => state.puzzlesSlice.allPuzzleTags)();
  const meta_tags = tags.filter((tag) => tag.is_meta && tag.name != name);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    api
      .updatePuzzle(huntId, puzzleId, {
        name: newName,
        url: newUrl,
        is_meta: newIsMeta,
        create_channels: createChannels,
      })
      .finally(hideModal);
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
            label="This is a meta"
            id="is-meta-checkbox"
            checked={newIsMeta}
            onChange={(e: ChangeEvent) => setNewIsMeta(e.target.checked)}
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
          {meta_tags.length > 0 ? (
            <>
              <h5 style={{ textAlign: "center" }}>Parent Metas</h5>
              <EditableTagList puzzleId={puzzleId} tags={meta_tags} />
            </>
          ) : undefined}
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="danger"
            onClick={() => {
              hideModal();
              showModal({
                type: "DELETE_PUZZLE",
                props: {
                  huntId,
                  puzzleId: puzzleId,
                  puzzleName: name,
                },
              });
            }}
            className="me-auto"
          >
            Delete Puzzle
          </Button>
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

export default EditPuzzleModal;
