import React from "react";
import { Button, Modal } from "react-bootstrap";
import { useTranslation, Trans } from "react-i18next";

import { useStore } from "./store";
import type { PuzzleId, HuntId } from "./types";

function DeletePuzzleModal({
  huntId,
  puzzleId,
  puzzleName,
}: {
  huntId: HuntId;
  puzzleId: PuzzleId;
  puzzleName: string;
}) {
  const { deletePuzzle } = useStore((state) => state.puzzlesSlice);
  const { hideModal } = useStore((state) => state.modalSlice);
  const { t } = useTranslation();

  const onDelete = () => {
    deletePuzzle(puzzleId).finally(hideModal);
  };

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>
          {t("delete-puzzle-title", {
            puzzleName,
          })}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Trans i18nKey="delete-puzzle-confirm" values={{ puzzleName }}>
          Are you sure you want to delete <b>{puzzleName}</b>?
        </Trans>
      </Modal.Body>
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

export default DeletePuzzleModal;
