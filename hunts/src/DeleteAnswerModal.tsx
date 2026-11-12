import React from "react";
import { Button, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";

import { useStore } from "./store";
import type { AnswerId, PuzzleId } from "./types";

function DeleteAnswerModal({
  puzzleId,
  answerId,
}: {
  puzzleId: PuzzleId;
  answerId: AnswerId;
}) {
  const { deleteAnswer } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);
  const { t } = useTranslation();

  const onDelete = () => {
    deleteAnswer(puzzleId, answerId).finally(hideModal);
  };

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>{t("delete-answer-title")}</Modal.Title>
      </Modal.Header>
      <Modal.Body>{t("delete-answer-confirm")}</Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={hideModal}>
          {t("cancel")}
        </Button>
        <Button variant="danger" onClick={onDelete}>
          {t("delete")}
        </Button>
      </Modal.Footer>
    </>
  );
}

export default DeleteAnswerModal;
