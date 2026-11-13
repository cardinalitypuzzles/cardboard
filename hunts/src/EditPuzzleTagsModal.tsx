import React, { FormEvent } from "react";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { DEFAULT_TAG_COLOR } from "./constants";
import ColorPicker from "./ColorPicker";
import TagDropdown from "./TagDropdown";
import EditableTagList from "./EditableTagList";
import { sortPuzzleTags } from "./utils";

import { useStore } from "./store";
import type { PuzzleId, PuzzleTag, TagId } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;
type ManageAction = "favorite" | "change-color" | "delete";

function EditPuzzleTagsModal({
  puzzleId,
  puzzleName,
}: {
  puzzleId: PuzzleId;
  puzzleName: string;
}) {
  const huntTags = useStore((state) => state.huntSlice.hunt.puzzle_tags);
  const puzzleTags = useStore((state) => state.puzzlesSlice.allPuzzleTags)();
  const puzzles = useStore((state) => state.puzzlesSlice.puzzles);
  const { addPuzzleTag, updateHuntTag, deleteHuntTag } = useStore(
    (state) => state.puzzlesSlice
  );
  const { favoriteTagNames, toggleFavoriteTag } = useStore(
    (state) => state.favoriteTagsSlice
  );
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

  const [selectedTagId, setSelectedTagId] = React.useState<string>("");
  const [manageAction, setManageAction] =
    React.useState<ManageAction>("favorite");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [manageError, setManageError] = React.useState<string | null>(null);

  const selectedTag =
    manageableTags.find((tag) => String(tag.id) === selectedTagId) ??
    manageableTags[0] ??
    null;

  const isSelectedFavorite = selectedTag
    ? favoriteTagNames.includes(selectedTag.name.trim().toLowerCase())
    : false;
  const selectedTagUsageCount = selectedTag
    ? Object.values(puzzles).filter((p) =>
        p.tags.some((tag) => tag.id === selectedTag.id)
      ).length
    : 0;

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
              color: DEFAULT_TAG_COLOR,
            }).then(() => {
              setNewTagName("");
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
            <Button
              variant="primary"
              type="submit"
              disabled={!newTagName.trim()}
            >
              {t("create")}
            </Button>
          </div>
        </Form>

        {selectedTag ? (
          <>
            <hr />
            <div className="d-flex align-items-start flex-column">
              <h5 className="align-self-center">{t("tags-manage")}</h5>
              <div className="d-flex align-items-center gap-2 w-100 my-1">
                <TagDropdown
                  tags={manageableTags}
                  selectedTag={selectedTag}
                  onSelect={(tag) => {
                    setSelectedTagId(String(tag.id));
                    setManageAction("favorite");
                    setManageError(null);
                  }}
                />
                <Form.Select
                  className="w-auto flex-grow-1"
                  value={manageAction}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                    setManageAction(e.target.value as ManageAction);
                    setManageError(null);
                  }}
                >
                  <option value="favorite">
                    {isSelectedFavorite
                      ? t("tag-action-unfavorite")
                      : t("tag-action-favorite")}
                  </option>
                  <option value="change-color">
                    {t("tag-action-change-color")}
                  </option>
                  <option value="delete">{t("tag-action-delete")}</option>
                </Form.Select>
              </div>

              {manageError ? (
                <Alert variant="danger" className="w-100 mt-2">
                  {manageError}
                </Alert>
              ) : null}

              {manageAction === "change-color" ? (
                <div className="mt-2">
                  <ColorPicker
                    value={selectedTag.color}
                    onChange={(color) => {
                      if (color === selectedTag.color || isSubmitting) {
                        return;
                      }
                      setIsSubmitting(true);
                      setManageError(null);
                      updateHuntTag(selectedTag.id, { color })
                        .catch((err: Error) => setManageError(err.message))
                        .finally(() => setIsSubmitting(false));
                    }}
                  />
                </div>
              ) : null}

              {manageAction === "favorite" ? (
                <div className="mt-2">
                  <Button
                    variant="primary"
                    onClick={() => toggleFavoriteTag(selectedTag.name)}
                  >
                    {isSelectedFavorite
                      ? t("tag-action-unfavorite")
                      : t("tag-action-favorite")}
                  </Button>
                </div>
              ) : null}

              {manageAction === "delete" ? (
                <div className="d-flex align-items-center gap-2 mt-2">
                  <span className="text-muted">
                    {t("tag-used-count", { count: selectedTagUsageCount })}
                  </span>
                  <Button
                    variant="danger"
                    disabled={isSubmitting}
                    onClick={() => {
                      setIsSubmitting(true);
                      setManageError(null);
                      deleteHuntTag(selectedTag.id, selectedTag.name)
                        .then(() => {
                          setSelectedTagId("");
                          setManageAction("favorite");
                        })
                        .catch((err: Error) => setManageError(err.message))
                        .finally(() => setIsSubmitting(false));
                    }}
                  >
                    {t("tag-action-delete")}
                  </Button>
                </div>
              ) : null}
            </div>
          </>
        ) : null}
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
