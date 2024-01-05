import React from "react";
import PropTypes from "prop-types";
import {
  useTable,
  useExpanded,
  useGlobalFilter,
  useFilters,
} from "react-table";
import { matchSorter } from "match-sorter";
import Table from "react-bootstrap/Table";
import { filterSolvedPuzzlesfn } from "./solveStateFilter";
import { useSelector } from "react-redux";
import { getTextFilter } from "./filterSlice";

import AnswerCell from "./AnswerCell";
import NameCell from "./NameCell";
import StatusCell from "./StatusCell";
import CreationCell from "./CreationCell";
import TagCell from "./TagCell";
import UsersCell from "./UsersCell";
import { LinkCell } from "./LinkCell";
import { getCollapsedPuzzles } from "./collapsedPuzzlesSlice";

const TABLE_COLUMNS = [
  {
    Header: "Name",
    accessor: "name",
    Cell: NameCell,
    className: "col-4",
  },
  {
    Header: "",
    accessor: (row) => row.recent_editors,
    Cell: UsersCell,
    id: "recentEditors",
  },
  {
    Header: "Answer",
    accessor: (row) => row.guesses.map(({ text }) => text).join(" "),
    Cell: AnswerCell,
    id: "answer",
    className: "col-2",
  },
  {
    Header: "Status",
    accessor: "status",
    Cell: StatusCell,
    filter: "solvedFilter",
    className: "col-1",
  },
  {
    Header: "Links",
    Cell: LinkCell,
    className: "col-1",
  },
  {
    Header: "Created",
    accessor: "created_on",
    Cell: CreationCell,
    className: "col-1",
  },
  {
    accessor: (row) => row.tags.map(({ name }) => name).join(" "),
    id: "tags",
  },
  {
    accessor: "is_meta",
    id: "is_meta",
  },
  {
    accessor: "id",
    id: "id",
  },
  {
    accessor: "url",
    id: "url",
  },
];

function textFilterFn(rows, id, filterValue) {
  if (!filterValue || !filterValue.length) {
    return rows;
  }

  const words = filterValue.split(" ");
  if (!words) {
    return rows;
  }
  const keys = ["values.name", "values.tags", "values.status", "values.answer"];
  // Need to clone these results because this library is broken as shit
  return words
    .reduceRight((results, word) => matchSorter(results, word, { keys }), rows)
    .map((row) => Object.assign({}, row));
}

textFilterFn.autoRemove = (val) => !val;

function filterPuzzlesByTagFn(rows, id, tagList) {
  return rows.filter((row) => {
    return tagList.every((tag) =>
      row.original.tags.map((x) => x.id).includes(tag.id)
    );
  });
}

function rowClassName(row) {
  switch (row.values.status) {
    case "SOLVED":
      return "table-success";
    case "STUCK":
      return "table-danger";
    case "EXTRACTION":
      return "table-danger";
    case "PENDING":
      return "table-warning";
    default:
      return "";
  }
}

export const PuzzleTable = React.memo(({ data, filterSolved, filterTags }) => {
  const filter = useSelector(getTextFilter);

  const filterTypes = React.useMemo(
    () => ({
      globalFilter: textFilterFn,
      solvedFilter: filterSolvedPuzzlesfn,
      tagsFilter: filterPuzzlesByTagFn,
    }),
    []
  );

  const getRowId = React.useCallback((row, _, parent) => {
    if (parent) {
      return `${parent.id}.${row.id}`;
    } else {
      return row.id.toString();
    }
  }, []);

  const collapsedPuzzles = useSelector(getCollapsedPuzzles(CURRENT_HUNT_ID));

  const {
    getTableProps,
    getTableBodyProps,
    allColumns,
    rows,
    prepareRow,
    setGlobalFilter,
    setFilter,
  } = useTable(
    {
      columns: TABLE_COLUMNS,
      data,
      filterTypes,
      getRowId,
      autoResetExpanded: false,
      autoResetGlobalFilter: false,
      globalFilter: "globalFilter",
      autoResetFilters: false,
      initialState: {
        hiddenColumns: ["tags", "is_meta", "id", "url"],
        filters: [],
        // Apparently our patch of react-table introduces the 'collapsed'
        // object that has the opposite semantics of the 'expanded' API.
        collapsed: collapsedPuzzles,
      },
    },
    useGlobalFilter,
    useExpanded,
    useFilters
  );

  React.useEffect(() => setGlobalFilter(filter), [filter]);

  // This pattern does not spark joy, but react-table only provides an imperative filter api.
  React.useEffect(() => {
    setFilter("status", filterSolved);
  }, [filterSolved]);

  React.useEffect(() => {
    setFilter("tags", filterTags);
  }, [filterTags]);

  return (
    <>
      <Table size="sm" {...getTableProps()}>
        <thead>
          <tr>
            {allColumns.map((column) =>
              column.isVisible ? (
                <th {...column.getHeaderProps()} className={column.className}>
                  {column.render("Header")}
                </th>
              ) : null
            )}
          </tr>
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row) => {
            prepareRow(row);
            return (
              <tr className={rowClassName(row)} {...row.getRowProps()}>
                {row.cells.map((cell) => {
                  return (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </Table>
    </>
  );
});

PuzzleTable.propTypes = {
  data: PropTypes.array.isRequired,
};
