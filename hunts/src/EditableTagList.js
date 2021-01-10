import React from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  addPuzzleTag,
  deletePuzzleTag,
  selectPuzzleById,
} from "./puzzlesSlice";
import TagPill from "./TagPill";

function EditableTagList({ puzzleId, tags }) {
  const selectPuzzleTags = React.useMemo(
    () => (state) => selectPuzzleById(state, puzzleId)["tags"],
    [puzzleId]
  );
  const puzzleTags = useSelector(selectPuzzleTags);
  const puzzleTagIds = new Set(puzzleTags.map((tag) => tag.id));
  const dispatch = useDispatch();
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      {tags.map((tag) => (
        <TagPill
          {...tag}
          puzzleId={puzzleId}
          editable={false}
          selected={puzzleTagIds.has(tag.id)}
          faded={!puzzleTagIds.has(tag.id)}
          key={tag.name}
          onClick={() => {
            if (puzzleTagIds.has(tag.id)) {
              dispatch(deletePuzzleTag({ puzzleId, tagId: tag.id }));
            } else {
              dispatch(
                addPuzzleTag({
                  ...tag,
                  puzzleId,
                })
              );
            }
          }}
        />
      ))}
    </div>
  );
}

export default EditableTagList;
