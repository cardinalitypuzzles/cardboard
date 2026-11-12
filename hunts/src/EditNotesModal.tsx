import React, { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";

import { useStore } from "./store";
import type { PuzzleId } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function EditNotesModal({
  puzzleId,
  text,
}: {
  puzzleId: PuzzleId;
  text: string;
}) {
  const { editNotes } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);
  const { t } = useTranslation();

  const [newNotes, setNewNotes] = React.useState(text);
  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    editNotes(puzzleId, newNotes).finally(hideModal);
    return false;
  };
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>{t("edit-notes-title")}</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit} autoComplete="off">
        <Modal.Body>
          <Form.Control
            required
            autoFocus
            placeholder={t("notes")}
            value={newNotes}
            onChange={(e: ChangeEvent) => setNewNotes(e.target.value)}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={hideModal}>
            {t("cancel")}
          </Button>
          <Button variant="primary" type="submit">
            {t("submit")}
          </Button>
        </Modal.Footer>
      </Form>
    </>
  );
}

export default EditNotesModal;
