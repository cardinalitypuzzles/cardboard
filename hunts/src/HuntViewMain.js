import React from "react";
import PropTypes from "prop-types";
import { PuzzleTable } from "./puzzle-table";
import useInterval from "@use-it/interval";
import Badge from "react-bootstrap/Badge";
import Button from "react-bootstrap/Button";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

const TABLE_COLUMNS = [
  {
    Header: "Name",
    accessor: "name",
    Cell: ({ row, value }) =>
      row.canExpand ? (
        <span
          {...row.getToggleRowExpandedProps({
            style: {
              paddingLeft: `${row.depth * 2}rem`,
            },
          })}
        >
          {row.isExpanded ? "▼" : "▶"} {value}
        </span>
      ) : (
        <span style={{ paddingLeft: `${row.depth * 2}rem` }}>{value}</span>
      ),
  },
  {
    Header: "Answer",
    accessor: "answer",
    Cell: ({ row, value }) => <span className="text-monospace">{value}</span>,
  },
  {
    Header: "Status",
    accessor: "status",
  },
  {
    Header: "Sheet",
    accessor: "sheet",
    Cell: ({ row, value }) =>
      value ? (
        <a href={value} target="_blank">
          Link
        </a>
      ) : null,
  },
  {
    Header: "Tags",
    id: "tags",
    accessor: (row) => row.tags.map(({ name }) => name).join(" "),
    Cell: ({ row, value }) => {
      if (row.original.tags && row.original.tags.length) {
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
          </>
        );
      } else {
        return null;
      }
    },
  },
  {
    Header: "Metas",
    id: "metas",
    Cell: ({ row, value }) => (
      <Button variant="outline-secondary">Assign Meta</Button>
    ),
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

  const huntApiUrl = `/api/v1/hunt/${props.huntId}`;
  const puzzlesApiUrl = `/api/v1/hunt/${props.huntId}/puzzles`;
  const updatePuzzleData = () => {
    fetch(puzzlesApiUrl)
      .then((response) => {
        if (response.status > 400) {
          // TODO: error handling
          console.error("Puzzles API failure", response);
        }
        return response.json();
      })
      .then((puzzleData) => {
        setPuzzleData(processPuzzleData(puzzleData));
      });
  };

  useInterval(updatePuzzleData, 10 * 1000);

  React.useEffect(() => {
    fetch(huntApiUrl)
      .then((response) => {
        if (response.status > 400) {
          //TODO: Some error handling should go here
          console.error("Hunt API failure", response);
        }
        return response.json();
      })
      .then((huntData) => {
        setHuntData(huntData);
      });

    updatePuzzleData();
  }, [props.huntId]);

  if (huntData) {
    return (
      <div>
        <h1>{huntData.name} - All Puzzles</h1>
        <PuzzleTable columns={TABLE_COLUMNS} data={puzzleData} />
      </div>
    );
  } else {
    return <h1>Loading...</h1>;
  }
};

HuntViewMain.propTypes = {
  huntId: PropTypes.string.isRequired,
};
