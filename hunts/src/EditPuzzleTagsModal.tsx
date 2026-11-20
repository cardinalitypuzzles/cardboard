import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { DEFAULT_TAG_COLOR } from "./constants";
import ColorPicker from "./ColorPicker";
import EditableTagList from "./EditableTagList";
import { sortPuzzleTags } from "./utils";

import { useStore } from "./store";
import type { PuzzleId, PuzzleTag, TagId } from "./types";

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
  const addPuzzleTag = useStore((state) => state.puzzlesSlice.addPuzzleTag);
  const hideModal = useStore((state) => state.modalSlice.hideModal);
  const { t } = useTranslation();

  // Use a map to concat huntTags and puzzleTags and then dedupe by id.
  const tagMap = new Map<TagId, PuzzleTag>();
  for (const tag of huntTags.concat(puzzleTags)) {
    tagMap.set(tag.id, tag);
  }
  const manageableTags = sortPuzzleTags(
    Array.from(tagMap.values()).filter((tag) => !tag.is_meta)
  );

  const [newTagName, setNewTagName] = React.useState("");
  const [newTagColor, setNewTagColor] =
    React.useState<string>(DEFAULT_TAG_COLOR);

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
        <h5 className="text-center">{t("tags")}</h5>
        <EditableTagList puzzleId={puzzleId} tags={manageableTags} />
        <br />
        <Form
          className="d-flex align-items-center flex-column w-100"
          onSubmit={(e: FormEvent) => {
            e.preventDefault();
            const trimmedName = newTagName.trim();
            if (!trimmedName) {
              return false;
            }
            addPuzzleTag(puzzleId, {
              name: trimmedName,
              color: newTagColor,
            }).then(() => {
              setNewTagName("");
              setNewTagColor(DEFAULT_TAG_COLOR);
            });
            return false;
          }}
        >
          <h5>{t("tags-create")}</h5>
          <div className="d-flex align-items-center gap-2 w-100">
            <Form.Control
              className="tag-name-input w-auto flex-grow-1"
              placeholder={t("tag-placeholder")}
              value={newTagName}
              onChange={(e: ChangeEvent) => setNewTagName(e.target.value)}
            />
            <ColorPicker value={newTagColor} onChange={setNewTagColor} />
            <Button
              variant="primary"
              type="submit"
              disabled={!newTagName.trim()}
            >
              {t("add")}
            </Button>
          </div>
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
