import React, { FormEvent } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { useTranslation } from "react-i18next";

import { useStore } from "./store";
import type { HuntId, PuzzleTag } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function AddPuzzleModal({ huntId }: { huntId: HuntId }) {
  const { t } = useTranslation();
  const [name, setName] = React.useState("");
  const [url, setUrl] = React.useState("");
  const [assignedMeta, setAssignedMeta] = React.useState("");
  const [isMeta, setIsMeta] = React.useState(false);
  const [createChannels, setCreateChannels] = React.useState(
    useStore((state) => state.huntSlice.hunt.create_channel_by_default)
  );

  const puzzleTags = useStore((state) => state.huntSlice.hunt.puzzle_tags);
  const { hideModal } = useStore((state) => state.modalSlice);
  const { addPuzzle } = useStore((state) => state.puzzlesSlice);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    addPuzzle({
      huntId,
      name,
      url,
      is_meta: isMeta,
      create_channels: createChannels,
      assigned_meta: assignedMeta,
    }).finally(hideModal);
    return false;
  };

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>{t("add-puzzle")}</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit} autoComplete="off">
        <Modal.Body>
          <Form.Group controlId="addPuzzle.name">
            <Form.Label>{t("puzzle-name")}</Form.Label>
            <Form.Control
              required
              placeholder={t("name-placeholder")}
              value={name}
              autoFocus
              onChange={(e: ChangeEvent) => setName(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="addPuzzle.url">
            <Form.Label>{t("puzzle-url")}</Form.Label>
            <Form.Control
              required
              placeholder={t("url-placeholder")}
              value={url}
              onChange={(e: ChangeEvent) => setUrl(e.target.value)}
            />
          </Form.Group>
          <Form.Group controlId="addPuzzle.meta">
            <Form.Label>{t("assigned-meta")}</Form.Label>
            <Form.Control
              as="select"
              value={assignedMeta}
              onChange={(e: ChangeEvent) => setAssignedMeta(e.target.value)}
            >
              <option key="none" value="">
                {t("none")}
              </option>
              {puzzleTags
                .filter((tag: PuzzleTag) => tag.is_meta)
                .map((tag: PuzzleTag, i: number) => (
                  <option key={tag.name} value={tag.name}>
                    {tag.name}
                  </option>
                ))}
            </Form.Control>
          </Form.Group>
          <Form.Check
            type="checkbox"
            label={t("is-meta")}
            id="is-meta-checkbox"
            checked={isMeta}
            onChange={(e: ChangeEvent) => setIsMeta(e.target.checked)}
          />
          <Form.Check
            type="checkbox"
            label={t("create-discord-channels")}
            id="create-channels-checkbox"
            checked={createChannels}
            onChange={(e: ChangeEvent) => setCreateChannels(e.target.checked)}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={hideModal}>
            {t("cancel")}
          </Button>
          <Button variant="primary" type="submit">
            {t("add")}
          </Button>
        </Modal.Footer>
      </Form>
    </>
  );
}

export default AddPuzzleModal;
