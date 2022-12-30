import Button from "react-bootstrap/Button";
import React from "react";
import { useDispatch } from "react-redux";
import { faEdit, faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { showModal } from "./modalSlice";
import ClickableIcon from "./ClickableIcon";

export default function AnswerCell({ row }) {
  const dispatch = useDispatch();
  if (row.original.guesses === undefined || row.original.guesses.length == 0) {
    return (
      <Button
        variant="outline-primary"
        onClick={() =>
          dispatch(
            showModal({
              type: "SUBMIT_ANSWER",
              props: {
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
        <React.Fragment key={text}>
          <span className="text-monospace">{text}</span>{" "}
          <ClickableIcon
            icon={faEdit}
            onClick={() =>
              dispatch(
                showModal({
                  type: "EDIT_ANSWER",
                  props: {
                    puzzleId: row.values.id,
                    answerId: id,
                    text,
                  },
                })
              )
            }
          />{" "}
          <ClickableIcon
            icon={faTrashAlt}
            onClick={() =>
              dispatch(
                showModal({
                  type: "DELETE_ANSWER",
                  props: {
                    puzzleId: row.values.id,
                    answerId: id,
                  },
                })
              )
            }
          />
          <br />
        </React.Fragment>
      ))}
      <ClickableIcon
        icon={faPlus}
        onClick={() =>
          dispatch(
            showModal({
              type: "SUBMIT_ANSWER",
              props: {
                puzzleId: row.values.id,
                puzzleName: row.values.name,
              },
            })
          )
        }
      />
    </>
  );
}
