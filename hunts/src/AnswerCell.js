import Button from "react-bootstrap/Button";
import React from "react";
import { updatePuzzle } from "./puzzlesSlice";
import { useSelector, useDispatch } from "react-redux";
import { showModal } from "./modalSlice";

export default function AnswerCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  console.log(row);
  if (row.original.guesses === undefined || row.original.guesses.length == 0) {
    return (
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
  return (
    <>
      {row.original.guesses.map(({ text }) => (
        <>
          <span className="text-monospace">{text}</span>
          <br />
        </>
      ))}
    </>
  );
}
