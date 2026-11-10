import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { DEFAULT_TAG_COLOR, SELECTABLE_TAG_COLORS } from "./constants";
import api from "./api";
import TagPill from "./TagPill";
import EditableTagList from "./EditableTagList";

import { useStore } from "./store";
import type { PuzzleId } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function EditPuzzleTagsModal({
  puzzleId,
  puzzleName,
}: {
  puzzleId: PuzzleId;
  puzzleName: string;
}) {
  const huntTags = useStore((state) => state.huntSlice.hunt.puzzle_tags);
  const puzzleTags = useStore((state) => state.puzzlesSlice.allPuzzleTags)();
  const hideModal = useStore((state) => state.modalSlice.hideModal);
  const { t } = useTranslation();

  // Use a map to concat huntTags and puzzleTags and then dedupe by id.
  const tagMap = new Map();
  for (const tag of huntTags.concat(puzzleTags)) {
    tagMap.set(tag.id, tag);
  }
  const allTags = Array.from(tagMap.values());

  const [newTagName, setNewTagName] = React.useState("");
  const [newTagColor, setNewTagColor] = React.useState(DEFAULT_TAG_COLOR);
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>
          {t("edit-tags-title", {
            puzzleName,
          })}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <h5 style={{ textAlign: "center" }}>{t("locations")}</h5>
        <EditableTagList
          puzzleId={puzzleId}
          tags={allTags.filter((tag) => tag.is_location)}
        />
        <br />
        <h5 style={{ textAlign: "center" }}>{t("tags")}</h5>
        <EditableTagList
          puzzleId={puzzleId}
          tags={allTags.filter((tag) => !tag.is_meta && !tag.is_location)}
        />
        <br />
        <Form
          style={{
            display: "flex",
            alignItems: "flex-start",
            flexDirection: "column",
          }}
          onSubmit={(e: FormEvent) => {
            e.preventDefault();
            api
              .addPuzzleTag(puzzleId, {
                name: newTagName,
                color: newTagColor,
              })
              .then(() => {
                setNewTagName("");
                setNewTagColor(DEFAULT_TAG_COLOR);
              });
            return false;
          }}
        >
          <h5 style={{ alignSelf: "center" }}>{t("tags-create")}</h5>
          <div style={{ alignSelf: "center", marginBottom: "3px" }}>
            <TagPill name={newTagName} color={newTagColor} />
          </div>
          <Form.Control
            placeholder={t("tag-placeholder")}
            value={newTagName}
            onChange={(e: ChangeEvent) => setNewTagName(e.target.value)}
            style={{ margin: "2px" }}
          />
          <Form.Control
            as="select"
            value={newTagColor}
            onChange={(e: ChangeEvent) => setNewTagColor(e.target.value)}
            style={{ margin: "2px" }}
          >
            {SELECTABLE_TAG_COLORS.map(({ color, key }) => (
              <option key={color} value={color}>
                {t(key)}
              </option>
            ))}
          </Form.Control>
          <Button variant="primary" type="submit">
            {t("create")}
          </Button>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="primary" type="submit" onClick={hideModal}>
          {t("done")}
        </Button>
      </Modal.Footer>
    </>
  );
}

export default EditPuzzleTagsModal;
