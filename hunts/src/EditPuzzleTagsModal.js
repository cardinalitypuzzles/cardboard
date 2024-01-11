import React from "react";
import { useDispatch, useSelector } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { addPuzzleTag, selectPuzzleTags } from "./puzzlesSlice";
import { selectHuntTags } from "./huntSlice";
import { DEFAULT_TAG_COLOR, SELECTABLE_TAG_COLORS } from "./constants";
import { hideModal } from "./modalSlice";
import TagPill from "./TagPill";
import EditableTagList from "./EditableTagList";

function EditPuzzleTagsModal({ puzzleId, puzzleName }) {
  const huntTags = useSelector(selectHuntTags);
  const puzzleTags = useSelector(selectPuzzleTags);
  // Use a map to concat huntTags and puzzleTags and then dedupe by id.
  const tagMap = new Map();
  for (const tag of huntTags.concat(puzzleTags)) {
    tagMap.set(tag.id, tag);
  }
  const allTags = Array.from(tagMap.values());

  const [newTagName, setNewTagName] = React.useState("");
  const [newTagColor, setNewTagColor] = React.useState(DEFAULT_TAG_COLOR);
  const dispatch = useDispatch();
  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Edit Tags for {puzzleName}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <h5 style={{ textAlign: "center" }}>Metas</h5>
        <EditableTagList
          puzzleId={puzzleId}
          tags={allTags.filter((tag) => tag.is_meta)}
        />
        <br />
        <h5 style={{ textAlign: "center" }}>Locations</h5>
        <EditableTagList
          puzzleId={puzzleId}
          tags={allTags.filter((tag) => tag.is_location)}
        />
        <br />
        <h5 style={{ textAlign: "center" }}>Tags</h5>
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
          onSubmit={(e) => {
            e.preventDefault();
            dispatch(
              addPuzzleTag({
                name: newTagName,
                color: newTagColor,
                puzzleId,
              })
            ).then(() => {
              setNewTagName("");
              setNewTagColor(DEFAULT_TAG_COLOR);
            });
            return false;
          }}
        >
          <h5 style={{ alignSelf: "center" }}>Create new tag</h5>
          <div style={{ alignSelf: "center", marginBottom: "3px" }}>
            <TagPill name={newTagName} color={newTagColor} editable={false} />
          </div>
          <Form.Control
            placeholder="Logic Puzzle"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            style={{ margin: "2px" }}
          />
          <Form.Control
            as="select"
            value={newTagColor}
            onChange={(e) => setNewTagColor(e.target.value)}
            style={{ margin: "2px" }}
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
