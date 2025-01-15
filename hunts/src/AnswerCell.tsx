import React from "react";
import { Button } from "react-bootstrap";
import { useDispatch } from "react-redux";
import { faEdit, faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { showModal } from "./modalSlice";
import ClickableIcon from "./ClickableIcon";

import type { Row } from "react-table";
import type { Dispatch } from "./store";
import type { Puzzle } from "./types";

export default function AnswerCell({ row }: { row: Row<Puzzle> }) {
  const dispatch = useDispatch<Dispatch>();
  const [uiHovered, setUiHovered] = React.useState<number[]>([]);
  if (row.original.guesses === undefined || row.original.guesses.length == 0) {
    return (
      <Button
        className="cb-btn-compact"
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
    <div style={{ padding: '3px 0px' }}>
      {row.original.guesses.map(({ id, text }) => (
        <div
          key={text}
          onMouseOver={() => {
            setUiHovered(uiHovered.concat(id));
          }}
          onMouseLeave={() => {
            setUiHovered(uiHovered.filter((x) => x != id));
          }}
          className="puzzle-answer"
        >
          <span className="text-monospace">{text}</span>{" "}
          <div
            style={{
              display: "inline-block",
              visibility: uiHovered.includes(id) ? "visible" : "hidden",
            }}
          >
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
            />{" "}
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
          </div>
          <br />
        </div>
      ))}
    </div>
  );
}
