import React from "react";
import PropTypes from "prop-types";
import { PuzzleTable } from "./puzzle-table";
import NameCell from "./NameCell";
import { getHunt, getPuzzles, deletePuzzle } from "./api";
import useInterval from "@use-it/interval";
import Badge from "react-bootstrap/Badge";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";
import Modal from "react-bootstrap/Modal";
import DropdownButton from "react-bootstrap/DropdownButton";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faTimes } from "@fortawesome/free-solid-svg-icons";

export const HuntContext = React.createContext({
  huntId: "",
  handleShow: () => void 0,
  handleClose: () => void 0,
});

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

function puzzleComparator(a, b) {
  // Solved puzzles should appear below unsolved ones
  if (a.status == "SOLVED" && b.status != "SOLVED") {
    return 1;
  } else if (b.status == "SOLVED" && a.status != "SOLVED") {
    return -1;
  }
  // Feeders before metas
  if (a.feeders.length == 0 && b.feeders.length > 0) {
    return -1;
  } else if (a.feeders.length > 0 && b.feeders.length == 0) {
    return 1;
  }
  // Newer puzzles before old ones
  // TODO: once creation times are added to puzzles, use those instead
  return b.id - a.id;
}

function processPuzzleData(puzzleData) {
  const rowMap = {};
  puzzleData.forEach((row) => {
    rowMap[row.id] = row;
  });
  puzzleData.forEach((row) => {
    if (row.feeders.length > 0) {
      row.subRows = [];
      row.feeders.forEach((subRowId) => {
        row.subRows.push(rowMap[subRowId]);
      });
    }
  });
  puzzleData.forEach((row) => {
    if (row.subRows) {
      row.subRows.sort(puzzleComparator);
    }
  });
  const rows = Object.values(rowMap).filter((row) => row.metas.length == 0);
  rows.sort(puzzleComparator);
  return rows;
}

export const HuntViewMain = (props) => {
  const [huntData, setHuntData] = React.useState(props);
  const [puzzleData, setPuzzleData] = React.useState([]);
  const [modalContents, setModalContents] = React.useState(null);
  const [showModal, setShowModal] = React.useState(false);

  const updatePuzzleData = () => {
    getPuzzles(props.huntId).then((puzzleData) => {
      setPuzzleData(processPuzzleData(puzzleData));
    });
  };

  useInterval(updatePuzzleData, 10 * 1000);

  React.useEffect(() => {
    getHunt(props.huntId).then((huntData) => {
      setHuntData(huntData);
    });

    updatePuzzleData();
  }, [props.huntId]);

  const handleShow = ({ contents }) => {
    setModalContents(contents);
    setShowModal(true);
  };

  const handleClose = () => {
    setShowModal(false);
  };

  if (huntData) {
    return (
      <HuntContext.Provider
        value={{ huntId: props.huntId, handleShow, handleClose }}
      >
        <div>
          <h1>{huntData.name} - All Puzzles</h1>
          <PuzzleTable columns={TABLE_COLUMNS} data={puzzleData} />
        </div>
        <Modal show={showModal} onHide={handleClose}>
          {modalContents}
        </Modal>
      </HuntContext.Provider>
    );
  } else {
    return <h1>Loading...</h1>;
  }
};

HuntViewMain.propTypes = {
  huntId: PropTypes.string.isRequired,
};
