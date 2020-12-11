import React from "react";
import PropTypes from "prop-types";
import { useSelector, useDispatch } from "react-redux";
import { fetchPuzzles, selectPuzzleTableData } from "./puzzlesSlice";
import { fetchHunt } from "./huntSlice";
import { hideModal } from "./modalSlice";
import { PuzzleTable } from "./puzzle-table";
import NameCell from "./NameCell";
import DeletePuzzleModal from "./DeletePuzzleModal";
import api from "./api";
import useInterval from "@use-it/interval";
import Badge from "react-bootstrap/Badge";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";
import Modal from "react-bootstrap/Modal";
import DropdownButton from "react-bootstrap/DropdownButton";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faTimes } from "@fortawesome/free-solid-svg-icons";

const MODAL_COMPONENTS = {
  DELETE_PUZZLE: DeletePuzzleModal,
};

const TABLE_COLUMNS = [
  {
    Header: "Name",
    accessor: "name",
    Cell: NameCell,
  },
  {
    Header: "Answer",
    accessor: "answer",
    Cell: ({ row, value }) =>
      value ? (
        <span className="text-monospace">{value}</span>
      ) : (
        <Button variant="outline-primary">Submit Answer</Button>
      ),
  },
  {
    Header: "Status",
    accessor: "status",
    Cell: ({ row, value }) =>
      ["SOLVING", "STUCK", "EXTRACTION"].includes(value) ? (
        <DropdownButton
          id={`status-dropdown-${row.id}`}
          title={value}
          variant="outline-primary"
        >
          <Dropdown.Item>SOLVING</Dropdown.Item>
          <Dropdown.Item>STUCK</Dropdown.Item>
          <Dropdown.Item>EXTRACTION</Dropdown.Item>
        </DropdownButton>
      ) : (
        value
      ),
  },
  {
    Header: "Puzzle",
    accessor: "url",
    Cell: ({ row, value }) => (
      <a href={value} target="_blank">
        Puzzle
      </a>
    ),
  },
  {
    Header: "Sheet",
    accessor: "sheet",
    Cell: ({ row, value }) =>
      value ? (
        <a href={value} target="_blank">
          Sheet
        </a>
      ) : null,
  },
  {
    Header: "Tags",
    id: "tags",
    accessor: (row) => row.tags.map(({ name }) => name).join(" "),
    Cell: ({ row, value }) => {
      return (
        <>
          {row.original.tags.map(({ name, color }) => (
            <Badge pill variant={color} key={name}>
              {name}
              <span style={{ marginLeft: "5px", cursor: "pointer" }}>
                <FontAwesomeIcon icon={faTimes} />
              </span>
            </Badge>
          ))}
          <span style={{ cursor: "pointer" }}>
            <Badge pill variant="light">
              <FontAwesomeIcon icon={faPlus} />
            </Badge>
          </span>
        </>
      );
    },
  },
  {
    Header: "Metas",
    id: "metas",
    Cell: ({ row, value }) => (
      <Button variant="outline-secondary">Assign Meta</Button>
    ),
  },
  {
    accessor: "is_meta",
    id: "is_meta",
  },
  {
    accessor: "id",
    id: "id",
  },
];

export const HuntViewMain = (props) => {
  const tableData = useSelector(selectPuzzleTableData);
  const modal = useSelector((state) => state.modal);
  const hunt = useSelector((state) => state.hunt);
  const dispatch = useDispatch();

  const updatePuzzleData = () => {
    dispatch(fetchPuzzles(props.huntId));
  };

  useInterval(updatePuzzleData, 10 * 1000);

  const ModalComponent = MODAL_COMPONENTS[modal.type];
  React.useEffect(() => {
    dispatch(fetchHunt(props.huntId));
    updatePuzzleData();
  }, [props.huntId]);

  return (
    <div>
      <h1>{hunt.name} - All Puzzles</h1>
      <PuzzleTable columns={TABLE_COLUMNS} data={tableData} />
      <Modal show={modal.show} onHide={() => dispatch(hideModal())}>
        {ModalComponent ? <ModalComponent {...modal.props} /> : null}
      </Modal>
    </div>
  );
};

HuntViewMain.propTypes = {
  huntId: PropTypes.string.isRequired,
};
