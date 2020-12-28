import Badge from "react-bootstrap/Badge";
import Button from "react-bootstrap/Button";
import React from "react";
import { updatePuzzle } from "./puzzlesSlice";
import { useSelector, useDispatch } from "react-redux";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit, faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { showModal } from "./modalSlice";

export default function AnswerCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  console.log(row.original)
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
      {row.original.guesses.map(({ id, text }) => (
        <>
          <span className="text-monospace">{text}</span>
          <span
            style={{ cursor: "pointer" }}
            onClick={() =>
              dispatch(
                showModal({
                  type: "DELETE_ANSWER",
                  props: {
                    huntId,
                    puzzleId: row.values.id,
                    answerId: id,
                  },
                })
              )
            }
          >
            <Badge pill variant="light">
              <FontAwesomeIcon icon={faTrashAlt} />
            </Badge>
          </span>
          <br />
        </>
      ))}
    </>
  );
}
