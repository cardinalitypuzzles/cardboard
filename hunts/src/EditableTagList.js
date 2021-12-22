import React from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  addPuzzleTag,
  deletePuzzleTag,
  selectPuzzleById,
} from "./puzzlesSlice";
import { SELECTABLE_TAG_COLORS } from "./constants";
import TagPill from "./TagPill";

function EditableTagList({ puzzleId, tags }) {
  const selectPuzzleTags = React.useMemo(
    () => (state) => selectPuzzleById(state, puzzleId)["tags"],
    [puzzleId]
  );
  const puzzleTags = useSelector(selectPuzzleTags);
  const puzzleTagIds = new Set(puzzleTags.map((tag) => tag.id));
  const dispatch = useDispatch();


  const selectable_colors = SELECTABLE_TAG_COLORS.map((tag) => tag.color)
  const groupedTags = tags.reduce((result, item, index) => {
    if (result.length == 0) {
      result[0] = [item]
    } else if (!selectable_colors.includes(item.color)) {
      result[result.length - 1].push(item)
    } else if (result[result.length - 1][0].color == item.color) {
      result[result.length - 1].push(item)
    } else {
      result[result.length] = [item]
    }

    return result
  }, [])


  return (
    groupedTags.map((group) => (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        {
          group.map((tag) => (
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
          ))
        }
      </div>
    ))
  );
}

export default EditableTagList;
