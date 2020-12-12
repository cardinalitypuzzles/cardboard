import React from "react";
import Badge from "react-bootstrap/Badge";
import Button from "react-bootstrap/Button";
import { useSelector, useDispatch } from "react-redux";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit, faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { showModal } from "./modalSlice";

export default function NameCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const dispatch = useDispatch();
  return (
    <>
      {row.canExpand ? (
        <span
          {...row.getToggleRowExpandedProps({
            style: {
              paddingLeft: `${row.depth * 2}rem`,
            },
          })}
        >
          {row.isExpanded ? "▼" : "▶"} <b>{value}</b>
        </span>
      ) : (
        <span style={{ paddingLeft: `${row.depth * 2}rem` }}>
          <b>{value}</b>
        </span>
      )}{" "}
      {row.values.is_meta ? <Badge variant="dark">META</Badge> : null}
      <span
        style={{ cursor: "pointer" }}
        onClick={() =>
          dispatch(
            showModal({
              type: "EDIT_PUZZLE",
              props: {
                huntId,
                puzzleId: row.values.id,
                name: row.values.name,
                url: row.values.url,
                isMeta: row.values.is_meta,
              },
            })
          )
        }
      >
        <Badge pill variant="light">
          <FontAwesomeIcon icon={faEdit} />
        </Badge>
      </span>{" "}
      <span
        style={{ cursor: "pointer" }}
        onClick={() =>
          dispatch(
            showModal({
              type: "DELETE_PUZZLE",
              props: {
                huntId,
                puzzleId: row.values.id,
                puzzleName: value,
              },
            })
          )
        }
      >
        <Badge pill variant="light">
          <FontAwesomeIcon icon={faTrashAlt} />
        </Badge>
      </span>
    </>
  );
}
