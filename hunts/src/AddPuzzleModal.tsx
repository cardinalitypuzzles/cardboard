import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { addPuzzle } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";
import { selectHuntTags, selectHuntCreateChannelByDefault } from "./huntSlice";

import type { Dispatch } from "./store";
import type { HuntId, PuzzleTag } from "./types";
import { SafeButton, SafeForm, SafeModal } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function AddPuzzleModal({ huntId }: { huntId: HuntId }) {
  const allTags = useSelector(selectHuntTags);
  const [name, setName] = React.useState("");
  const [url, setUrl] = React.useState("");
  const [assignedMeta, setAssignedMeta] = React.useState("");
  const [isMeta, setIsMeta] = React.useState(false);
  const [createChannels, setCreateChannels] = React.useState(
    useSelector(selectHuntCreateChannelByDefault)
  );
  const dispatch = useDispatch<Dispatch>();
  const onSubmit = (e: ChangeEvent) => {
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
      <SafeModal.Header closeButton>
        <SafeModal.Title>Add Puzzle</SafeModal.Title>
      </SafeModal.Header>
      <SafeForm onSubmit={onSubmit}>
        <SafeModal.Body>
          <SafeForm.Group controlId="addPuzzle.name">
            <SafeForm.Label>Puzzle name</SafeForm.Label>
            <SafeForm.Control
              required
              placeholder="Name"
              value={name}
              autoFocus
              onChange={(e: ChangeEvent) => setName(e.target.value)}
            />
          </SafeForm.Group>
          <SafeForm.Group controlId="addPuzzle.url">
            <SafeForm.Label>Puzzle url</SafeForm.Label>
            <SafeForm.Control
              required
              placeholder="https://www.example.com/"
              value={url}
              onChange={(e: ChangeEvent) => setUrl(e.target.value)}
            />
          </SafeForm.Group>
          <SafeForm.Group controlId="addPuzzle.meta">
            <SafeForm.Label>Assigned Meta</SafeForm.Label>
            <SafeForm.Control
              as="select"
              value={assignedMeta}
              onChange={(e: ChangeEvent) => setAssignedMeta(e.target.value)}
            >
              <option key="none" value="">
                None
              </option>
              {allTags
                .filter((tag: PuzzleTag) => tag.is_meta)
                .map((tag: PuzzleTag, i: number) => (
                  <option key={tag.name} value={tag.name}>
                    {tag.name}
                  </option>
                ))}
            </SafeForm.Control>
          </SafeForm.Group>
          <SafeForm.Check
            type="checkbox"
            label="Is meta"
            id="is-meta-checkbox"
            checked={isMeta}
            onChange={(e: ChangeEvent) => setIsMeta(e.target.checked)}
          />
          <SafeForm.Check
            type="checkbox"
            label="Create discord channels"
            id="create-channels-checkbox"
            checked={createChannels}
            onChange={(e: ChangeEvent) => setCreateChannels(e.target.checked)}
          />
        </SafeModal.Body>
        <SafeModal.Footer>
          <SafeButton variant="secondary" onClick={() => dispatch(hideModal())}>
            Cancel
          </SafeButton>
          <SafeButton variant="primary" type="submit">
            Add
          </SafeButton>
        </SafeModal.Footer>
      </SafeForm>
    </>
  );
}

export default AddPuzzleModal;
