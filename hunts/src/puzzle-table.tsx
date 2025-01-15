import React from "react";
import {
  useTable,
  useExpanded,
  useGlobalFilter,
  useFilters,
} from "react-table";
import { Table } from "react-bootstrap";
import { matchSorter } from "match-sorter";
import { filterSolvedPuzzlesFn } from "./solveStateFilter";
import { useSelector } from "react-redux";
import { getTextFilter } from "./filterSlice";

import AnswerCell from "./AnswerCell";
import CreationCell from "./CreationCell";
import NameCell from "./NameCell";
import NotesCell from "./NotesCell";
import StatusCell from "./StatusCell";
import TagCell from "./TagCell";
import UsersCell from "./UsersCell";
import { LinkCell } from "./LinkCell";
import { getCollapsedPuzzles } from "./collapsedPuzzlesSlice";

import type { Puzzle, PuzzleTag, Row } from "./types";
import type { Row as BaseRow } from "react-table";

// The react-table typing is a mess for our current version
// (it's probably fine if we upgrade) and seems to be underpowered for
// the set of features it actually exposes. Around sensitive areas, we
// just use any to avoid fighting with the type system.

interface TableColumnFormat {
  Header?: string;
  Cell?: any;
  id?: string;
  filter?: string;
  className?: string;
  accessor?: string | ((row: Puzzle) => any);
}

const TABLE_COLUMNS: TableColumnFormat[] = [
  {
    Header: "Name",
    accessor: "name",
    Cell: NameCell as any,
    className: "col-2",
  },
  {
    Header: "Links",
    Cell: LinkCell,
    className: "col-1",
  },
  {
    Header: "Tags",
    id: "tags",
    Cell: TagCell,
    className: "col-2",
    accessor: (row) => row.tags.map(({ name }) => name).join(" "),
    filter: "tagsFilter",
  },
  {
    Header: "Notes",
    id: "notes",
    Cell: NotesCell,
    className: "col-2",
    accessor: (row) => row.notes,
  },
  {
    accessor: "last_edited_on",
    id: "last_edited_on",
  },
  {
    Header: "",
    accessor: (row) => row.recent_editors,
    Cell: UsersCell,
    id: "recentEditors",
  },
  {
    accessor: "top_editors",
    id: "topEditors",
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
    Header: "Created",
    accessor: "created_on",
    Cell: CreationCell,
    className: "col-1",
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

function textFilterFn(rows: Row<Puzzle>[], _: string, filterValue: string) {
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

textFilterFn.autoRemove = (val: any) => !val;

function filterPuzzlesByTagFn(
  rows: Row<Puzzle>[],
  _: string,
  tagList: PuzzleTag[]
) {
  return rows.filter((row) => {
    return tagList.every((tag) =>
      row.original.tags.map((x) => x.id).includes(tag.id)
    );
  });
}

function rowClassName(row: Row<Puzzle>) {
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
  ({
    data,
    filterSolved,
    filterTags,
  }: {
    data: any;
    filterSolved: number;
    filterTags: PuzzleTag[];
  }) => {
    const filter = useSelector(getTextFilter);

    const filterTypes = React.useMemo(
      () => ({
        globalFilter: textFilterFn,
        solvedFilter: filterSolvedPuzzlesFn,
        tagsFilter: filterPuzzlesByTagFn,
      }),
      []
    );

    const getRowId = React.useCallback(
      (row: Puzzle, _: any, parent: BaseRow<Puzzle> | undefined) => {
        if (parent) {
          return `${parent.id}.${row.id}`;
        } else {
          return row.id.toString();
        }
      },
      []
    );

    const collapsedPuzzles = useSelector(
      getCollapsedPuzzles(CURRENT_HUNT_ID.toString())
    );

    const {
      getTableProps,
      getTableBodyProps,
      allColumns,
      rows,
      prepareRow,
      setGlobalFilter,
      setFilter,
    }: any = useTable<Puzzle>(
      {
        columns: TABLE_COLUMNS as any,
        data,
        filterTypes,
        getRowId,
        autoResetExpanded: false,
        autoResetGlobalFilter: false,
        globalFilter: "globalFilter",
        autoResetFilters: false,
        initialState: {
          hiddenColumns: [
            "is_meta",
            "id",
            "url",
            "topEditors",
            "last_edited_on",
          ],
          // @ts-ignore
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

    let rowsList: React.ReactNode[] = [];
    const roundColors = [
      "crimson",
      "dodgerblue",
      "forestgreen",
      "darkorchid",
      "darkorange",
      "goldenrod",
      "coral",
      "darkslategray",
      "powderblue",
      "aquamarine",
      "palevioletred",
      "indigo",
      "olive",
      "violet",
    ];

    const topLevelId = (row: Row<Puzzle>) => parseInt(row.id.split(".")[0]);

    rows.forEach((row: Row<Puzzle>, i: number) => {
      prepareRow(row);

      // Add coloring and space between top-level metas
      if (i == 0 || topLevelId(row) != topLevelId(rows[i - 1] as Row<Puzzle>)) {
        if (i > 0) {
          rowsList.push(
            <tr key={`spacer-${row.id}`} style={{ height: "20px" }}></tr>
          );
        }

        rowsList.push(
          <tr key={`header-${row.id}`}>
            <td
              className="table-top-colorbar"
              colSpan={row.cells.length + 1}
              style={{
                background: `linear-gradient(90deg, ${
                  roundColors[topLevelId(row) % roundColors.length]
                }, transparent)`,
              }}
            ></td>
          </tr>
        );
      }

      rowsList.push(
        <tr className={rowClassName(row)} {...row.getRowProps()}>
          <td
            className="table-side-colorbar"
            style={{
              backgroundColor:
                roundColors[topLevelId(row) % roundColors.length],
            }}
          ></td>
          {row.cells.map((cell: any) => {
            return <td {...cell.getCellProps()}>{cell.render("Cell")}</td>;
          })}
        </tr>
      );
    });

    return (
      <>
        <Table size="sm" {...getTableProps()}>
          <thead>
            <tr>
              <th className="table-side-colorbar"></th>
              {allColumns.map((column: any) =>
                column.isVisible ? (
                  <th {...column.getHeaderProps()} className={column.className}>
                    {column.render("Header")}
                  </th>
                ) : null
              )}
            </tr>
          </thead>
          <tbody {...getTableBodyProps()}>{rowsList}</tbody>
        </Table>
      </>
    );
  }
);
