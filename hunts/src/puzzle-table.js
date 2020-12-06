import React from "react";
import PropTypes from "prop-types";
import { useTable, useExpanded, useGlobalFilter } from "react-table";
import { matchSorter } from "match-sorter";

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

export function PuzzleTable({ columns, data }) {
  const filterTypes = React.useMemo(
    () => ({
      globalFilter: textFilterFn,
    }),
    []
  );

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
  } = useTable(
    {
      columns,
      data,
      filterTypes,
      autoResetExpanded: false,
      globalFilter: "globalFilter",
    },
    useGlobalFilter,
    useExpanded
  );

  React.useEffect(() => toggleAllRowsExpanded(true), [data]);

  return (
    <>
      <GlobalFilter
        globalFilter={state.globalFilter}
        setGlobalFilter={setGlobalFilter}
      />
      <table {...getTableProps()}>
        <thead>
          <tr>
            {allColumns.map((column) => (
              <th {...column.getHeaderProps()}>{column.render("Header")}</th>
            ))}
          </tr>
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row, i) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map((cell) => {
                  return (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}

PuzzleTable.propTypes = {
  columns: PropTypes.array.isRequired,
  data: PropTypes.array.isRequired,
};

function GlobalFilter({ globalFilter, setGlobalFilter }) {
  const [value, setValue] = React.useState(globalFilter);

  return (
    <span>
      <input
        value={value || ""}
        onChange={(e) => {
          setValue(e.target.value);
          setGlobalFilter(e.target.value);
        }}
        placeholder={"Search"}
      />
    </span>
  );
}
