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
import { DEFAULT_TAG_COLOR, SELECTABLE_TAG_COLORS } from "./constants";
import { hideModal } from "./modalSlice";
import TagPill from "./TagPill";

function EditPuzzleTagsModal({ huntId, puzzleId }) {
  const selectPuzzleTags = React.useMemo(
    () => (state) => selectPuzzleById(state, puzzleId)["tags"],
    [puzzleId]
  );
  const puzzleTags = useSelector(selectPuzzleTags);
  const allTags = useSelector(selectAllTags);
  const [newTagName, setNewTagName] = React.useState("");
  const [newTagColor, setNewTagColor] = React.useState(DEFAULT_TAG_COLOR);
  const dispatch = useDispatch();
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Tags</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>
          Add metas:
          {allTags
            .filter((tag) => tag.is_meta)
            .map((tag) => (
              <TagPill
                {...tag}
                puzzleId={puzzleId}
                editable={false}
                key={tag.name}
                style={{ cursor: "pointer" }}
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
          Add tags:{" "}
          {allTags
            .filter((tag) => !tag.is_meta)
            .map((tag) => (
              <TagPill
                {...tag}
                puzzleId={puzzleId}
                editable={false}
                key={tag.name}
                style={{ cursor: "pointer" }}
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
        <Form
          onSubmit={(e) => {
            e.preventDefault();
            dispatch(
              addPuzzleTag({
                name: newTagName,
                color: newTagColor,
                huntId,
                puzzleId,
              })
            ).then(() => {
              setNewTagName("");
              setNewTagColor(DEFAULT_TAG_COLOR);
            });
            return false;
          }}
        >
          <Form.Label>Create new tag: </Form.Label>
          <TagPill name={newTagName} color={newTagColor} editable={false} />
          <Form.Control
            placeholder="Logic Puzzle"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
          />
          <Form.Control
            as="select"
            value={newTagColor}
            onChange={(e) => setNewTagColor(e.target.value)}
          >
            {SELECTABLE_TAG_COLORS.map(({ color, display }) => (
              <option key={color} value={color}>
                {display}
              </option>
            ))}
          </Form.Control>
          <Button variant="primary" type="submit">
            Create
          </Button>
        </Form>
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
