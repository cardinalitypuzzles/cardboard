import React from "react";
import PropTypes from "prop-types";
import { PuzzleTable } from "./puzzle-table.js";

const TABLE_COLUMNS = [
  {
    Header: "id",
    accessor: "id",
  },
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
  },
  {
    Header: "Status",
    accessor: "status",
  },
  {
    Header: "Sheet",
    accessor: "sheet",
  },
  {
    Header: "Tags",
    id: "tags",
  },
  {
    Header: "Metas",
    accessor: "metas",
  },
  {
    Header: "Feeders",
    accessor: "feeders",
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

  React.useEffect(() => {
    const huntApiUrl = `/api/v1/hunt/${props.huntId}`;
    const puzzlesApiUrl = `/api/v1/hunt/${props.huntId}/puzzles`;
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
