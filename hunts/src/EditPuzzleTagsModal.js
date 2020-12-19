import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import {
  addPuzzleTag,
  updatePuzzle,
  selectPuzzleById,
  selectAllTags,
} from "./puzzlesSlice";
import { hideModal } from "./modalSlice";
import TagPill from "./TagPill";

function EditPuzzleTagsModal({ huntId, puzzleId }) {
  const selectPuzzleTags = React.useMemo(
    () => (state) => selectPuzzleById(state, puzzleId)["tags"],
    [puzzleId]
  );
  const puzzleTags = useSelector(selectPuzzleTags);
  const allTags = useSelector(selectAllTags);
  const dispatch = useDispatch();
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Tags</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>
          All tags:{" "}
          {allTags.map((tag) => (
            <TagPill
              {...tag}
              puzzleId={puzzleId}
              editable={false}
              key={tag.name}
              onClick={() =>
                dispatch(
                  addPuzzleTag({
                    ...tag,
                    huntId,
                    puzzleId,
                  })
                )
              }
            />
          ))}
        </p>
        <p>
          Current tags:{" "}
          {puzzleTags.map((tag) => (
            <TagPill {...tag} puzzleId={puzzleId} key={tag.name} />
          ))}
        </p>
      </Modal.Body>
      <Modal.Footer>
        <Button
          variant="primary"
          type="submit"
          onClick={() => dispatch(hideModal())}
        >
          Done
        </Button>
      </Modal.Footer>
    </>
  );
}

export default EditPuzzleTagsModal;
