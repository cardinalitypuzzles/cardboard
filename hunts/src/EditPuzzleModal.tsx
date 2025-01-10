import React from "react";
import { useDispatch } from "react-redux";
import { updatePuzzle } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

import type { Dispatch } from "./store";
import type { HuntId, PuzzleId } from "./types";
import { SafeButton, SafeForm, SafeModal } from "./types";

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
  const onSubmit = (e: ChangeEvent) => {
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
      <SafeModal.Header closeButton>
        <SafeModal.Title>Edit Puzzle</SafeModal.Title>
      </SafeModal.Header>
      <SafeForm onSubmit={onSubmit}>
        <SafeModal.Body>
          <SafeForm.Group controlId="editPuzzle.name">
            <SafeForm.Label>Puzzle name</SafeForm.Label>
            <SafeForm.Control
              required
              autoFocus
              placeholder="Name"
              value={newName}
              onChange={(e: ChangeEvent) => setNewName(e.target.value)}
            />
          </SafeForm.Group>
          <SafeForm.Group controlId="editPuzzle.url">
            <SafeForm.Label>Puzzle url</SafeForm.Label>
            <SafeForm.Control
              required
              placeholder="https://www.example.com/"
              value={newUrl}
              onChange={(e: ChangeEvent) => setNewUrl(e.target.value)}
            />
          </SafeForm.Group>
          <SafeForm.Check
            type="checkbox"
            label="Is meta"
            id="is-meta-checkbox"
            checked={newIsMeta}
            onChange={(e: ChangeEvent) => setNewIsMeta(e.target.checked)}
          />
          <SafeForm.Check
            type="checkbox"
            label="Create discord channels"
            id="create-channels-checkbox"
            checked={createChannels}
            onChange={(e: ChangeEvent) => setCreateChannels(e.target.checked)}
            // If channel is already created, disable its deletion
            disabled={hasChannels}
          />
        </SafeModal.Body>
        <SafeModal.Footer>
          <SafeButton variant="secondary" onClick={() => dispatch(hideModal())}>
            Cancel
          </SafeButton>
          <SafeButton variant="primary" type="submit">
            Submit
          </SafeButton>
        </SafeModal.Footer>
      </SafeForm>
    </>
  );
}

export default EditPuzzleModal;
