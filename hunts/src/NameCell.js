import React from "react";
import Badge from "react-bootstrap/Badge";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit, faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { HuntContext } from "./HuntViewMain";
import { deletePuzzle } from "./api";

export default function ({ row, value }) {
  const { huntId, handleShow, handleClose } = React.useContext(HuntContext);
  const handleDelete = () => {
    deletePuzzle(huntId, row.values.id)
      .catch((error) => {
        // TODO: better error handling
        console.log(error);
      })
      .finally(handleClose);
  };
  const deletePuzzleModalContents = () => (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Delete {value}</Modal.Title>
      </Modal.Header>
      <Modal.Body>Are you sure you want to delete this puzzle?</Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="danger" onClick={handleDelete}>
          Delete
        </Button>
      </Modal.Footer>
    </>
  );
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
      <span style={{ cursor: "pointer" }}>
        <Badge pill variant="light">
          <FontAwesomeIcon icon={faEdit} />
        </Badge>
      </span>{" "}
      <span
        style={{ cursor: "pointer" }}
        onClick={() => handleShow({ contents: deletePuzzleModalContents() })}
      >
        <Badge pill variant="light">
          <FontAwesomeIcon icon={faTrashAlt} />
        </Badge>
      </span>
    </>
  );
}
