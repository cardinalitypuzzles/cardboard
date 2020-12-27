import Button from "react-bootstrap/Button";
import React from "react";
import { updatePuzzle } from "./puzzlesSlice";
import { useSelector, useDispatch } from "react-redux";
import { showModal } from "./modalSlice";

export default function AnswerCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  return value ? (
    <span className="text-monospace">{value}</span>
  ) : (
    <Button
      variant="outline-primary"
      onClick={() =>
        dispatch(
          showModal({
            type: "SUBMIT_ANSWER",
            props: {
              huntId,
              puzzleId: row.values.id,
              puzzleName: row.values.name,
            },
          })
        )
      }
    >
      Submit Answer
    </Button>
  );
}
