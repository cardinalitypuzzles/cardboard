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
import { filterPuzzlesByTagFn } from "./tagFilter";

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

export const PuzzleTable = React.memo(
  ({ columns, data, filter, filterSolved, filterTags, toggleTagInFilter }) => {
    const filterTypes = React.useMemo(
      () => ({
        globalFilter: textFilterFn,
        solvedFilter: filterSolvedPuzzlesfn,
        tagsFilter: filterPuzzlesByTagFn,
      }),
      []
    );

    const getRowId = React.useCallback((row, relativeIndex, parent) => {
      if (parent) {
        return `${parent.id}.${row.id}`;
      } else {
        return row.id.toString();
      }
    }, []);
    const {
      getTableProps,
      getTableBodyProps,
      allColumns,
      rows,
      state,
      prepareRow,
      toggleAllRowsExpanded,
      flatRows,
      preGlobalFilteredRows,
      setGlobalFilter,
      setFilter,
    } = useTable(
      {
        columns,
        data,
        filterTypes,
        getRowId,
        autoResetExpanded: false,
        autoResetGlobalFilter: false,
        globalFilter: "globalFilter",
        autoResetFilters: false,
        initialState: {
          hiddenColumns: ["is_meta", "id"],
          filters: [],
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
                  <th {...column.getHeaderProps()}>
                    {column.render("Header")}
                  </th>
                ) : null
              )}
            </tr>
          </thead>
          <tbody {...getTableBodyProps()}>
            {rows.map((row, i) => {
              prepareRow(row);
              row.original.toggleTagInFilter = toggleTagInFilter;
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
  }
);

PuzzleTable.propTypes = {
  columns: PropTypes.array.isRequired,
  data: PropTypes.array.isRequired,
};
