import React from "react";
import { useTranslation } from "react-i18next";
import {
  columnFilteringFeature,
  constructRow,
  createColumnHelper,
  createExpandedRowModel,
  globalFilteringFeature,
  metaHelper,
  rowExpandingFeature,
  tableFeatures,
  tableMemo,
  useTable,
} from "@tanstack/react-table";
import type {
  ColumnFiltersState,
  ExpandedState,
  Row,
  RowModel,
  Table,
  TableFeatures,
} from "@tanstack/react-table";
import { Table as BootstrapTable } from "react-bootstrap";
import { matchSorter } from "match-sorter";
import { filterRowsBySolveState } from "./solveStateFilter";
import type { SOLVE_STATE_FILTER_OPTIONS } from "./filterSlice";

import AnswerCell from "./AnswerCell";
import CreationCell from "./CreationCell";
import NameCell from "./NameCell";
import NotesCell from "./NotesCell";
import StatusCell from "./StatusCell";
import TagCell from "./TagCell";
import UsersCell from "./UsersCell";
import { LinkCell } from "./LinkCell";

import { useStore } from "./store";
import type { Puzzle, PuzzleRow, PuzzleTag } from "./types";

function collectFlatRows<TFeatures extends TableFeatures>(
  rows: Row<TFeatures, Puzzle>[],
  flatRows: Row<TFeatures, Puzzle>[],
  rowsById: Record<string, Row<TFeatures, Puzzle>>
) {
  for (const row of rows) {
    flatRows.push(row);
    rowsById[row.id] = row;
    if (row.subRows.length > 0) {
      collectFlatRows(row.subRows, flatRows, rowsById);
    }
  }
}

function createPuzzleFilteredRowModel<TFeatures extends TableFeatures>(): (
  table: Table<TFeatures, Puzzle>
) => () => RowModel<TFeatures, Puzzle> {
  return (table) =>
    tableMemo({
      feature: "columnFilteringFeature",
      table,
      fnName: "table.getFilteredRowModel",
      memoDeps: () => [
        table.getPreFilteredRowModel(),
        (
          table.atoms as { columnFilters?: { get: () => ColumnFiltersState } }
        ).columnFilters?.get(),
        (
          table.atoms as { globalFilter?: { get: () => unknown } }
        ).globalFilter?.get(),
      ],
      fn: () => _createPuzzleFilteredRowModel(table),
    });
}

function _createPuzzleFilteredRowModel<TFeatures extends TableFeatures>(
  table: Table<TFeatures, Puzzle>
): RowModel<TFeatures, Puzzle> {
  const rowModel = table.getPreFilteredRowModel();
  const atoms = table.atoms as {
    columnFilters?: { get: () => ColumnFiltersState };
    globalFilter?: { get: () => unknown };
  };
  const columnFilters = atoms.columnFilters?.get() ?? [];
  const globalFilter = (atoms.globalFilter?.get() as string) ?? "";

  const solveState = columnFilters.find((f) => f.id === "status")?.value as
    | SOLVE_STATE_FILTER_OPTIONS
    | undefined;
  const filterTags =
    (columnFilters.find((f) => f.id === "tags")?.value as
      | PuzzleTag[]
      | undefined) ?? [];

  if (
    !rowModel.rows.length ||
    (!solveState && !filterTags.length && !globalFilter)
  ) {
    return rowModel;
  }

  const cloneRow = (
    row: Row<TFeatures, Puzzle>,
    subRows: Row<TFeatures, Puzzle>[]
  ): Row<TFeatures, Puzzle> =>
    constructRow(
      table,
      row.id,
      row.original,
      row.index,
      row.depth,
      subRows,
      row.parentId
    );

  let filteredRows = filterRowsBySolveState(
    rowModel.rows,
    solveState as SOLVE_STATE_FILTER_OPTIONS,
    cloneRow
  );

  if (filterTags.length > 0 || globalFilter) {
    let candidateFlatRows: Row<TFeatures, Puzzle>[] = [];
    collectFlatRows(filteredRows, candidateFlatRows, {});

    if (filterTags.length > 0) {
      candidateFlatRows = candidateFlatRows.filter((row) =>
        filterTags.every((tag) =>
          row.original.tags.some((t) => t.id === tag.id)
        )
      );
    }

    if (globalFilter) {
      const words = globalFilter.split(" ");
      const keys = [
        (row: Row<TFeatures, Puzzle>) => row.original.name,
        (row: Row<TFeatures, Puzzle>) =>
          row.original.tags.map(({ name }) => name).join(" "),
        (row: Row<TFeatures, Puzzle>) => row.original.status,
        (row: Row<TFeatures, Puzzle>) =>
          row.original.guesses.map(({ text }) => text).join(" "),
      ];
      candidateFlatRows = words.reduceRight(
        (results, word) => matchSorter(results, word, { keys }),
        candidateFlatRows
      );
    }

    // Keep matching children nested under matching parents, and hide
    // non-matching parent metas by promoting their matching children.
    const matchedIds = new Set(candidateFlatRows.map((row) => row.id));
    filteredRows = candidateFlatRows.filter(
      (row) => !row.parentId || !matchedIds.has(row.parentId)
    );
  }

  const flatRows: Row<TFeatures, Puzzle>[] = [];
  const rowsById: Record<string, Row<TFeatures, Puzzle>> = {};
  collectFlatRows(filteredRows, flatRows, rowsById);
  return {
    rows: filteredRows,
    flatRows,
    rowsById,
  };
}

export const puzzleTableFeatures = tableFeatures({
  columnFilteringFeature,
  globalFilteringFeature,
  rowExpandingFeature,
  columnMeta: metaHelper<{ className?: string }>(),
  filteredRowModel: createPuzzleFilteredRowModel<any>(),
  expandedRowModel: createExpandedRowModel(),
});

const columnHelper = createColumnHelper<typeof puzzleTableFeatures, Puzzle>();

function rowClassName(row: PuzzleRow) {
  switch (row.original.status) {
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

function buildExpandedState(
  data: Puzzle[],
  collapsedPuzzles: Record<string, boolean>
): ExpandedState {
  const expanded: Record<string, boolean> = {};
  const walk = (items: Puzzle[], parentId?: string) => {
    for (const item of items) {
      const rowId = parentId ? `${parentId}.${item.id}` : item.id.toString();
      const { subRows } = item as Puzzle & { subRows?: Puzzle[] };
      if (subRows && subRows.length > 0) {
        if (!collapsedPuzzles[rowId]) {
          expanded[rowId] = true;
        }
        walk(subRows, rowId);
      }
    }
  };
  walk(data);
  return expanded;
}

export const PuzzleTable = React.memo(
  ({
    data,
    filterSolved,
    filterTags,
  }: {
    data: Puzzle[];
    filterSolved: number;
    filterTags: PuzzleTag[];
  }) => {
    const { t } = useTranslation();
    const filter = useStore((state) => state.filterSlice.filterValue);
    const collapsedPuzzles = useStore((state) =>
      state.collapsedPuzzlesSlice.getCollapsedPuzzles(
        CURRENT_HUNT_ID.toString()
      )
    );

    const columns = React.useMemo(
      () =>
        columnHelper.columns([
          columnHelper.accessor("name", {
            header: t("table-puzzle-name"),
            cell: ({ row, getValue }) => (
              <NameCell row={row} value={getValue()} />
            ),
            meta: { className: "col-2" },
          }),
          columnHelper.display({
            id: "links",
            header: t("table-puzzle-links"),
            cell: ({ row }) => <LinkCell row={row} />,
            meta: { className: "col-1" },
          }),
          columnHelper.accessor(
            (row) => row.tags.map(({ name }) => name).join(" "),
            {
              id: "tags",
              header: t("table-puzzle-tags"),
              cell: ({ row }) => <TagCell row={row} />,
              meta: { className: "col-2" },
            }
          ),
          columnHelper.accessor((row) => row.notes, {
            id: "notes",
            header: t("table-puzzle-notes"),
            cell: ({ row, getValue }) => (
              <NotesCell row={row} value={getValue()} />
            ),
            meta: { className: "col-2" },
          }),
          columnHelper.accessor((row) => row.recent_editors, {
            id: "recentEditors",
            header: "",
            cell: ({ row }) => <UsersCell row={row} />,
          }),
          columnHelper.accessor(
            (row) => row.guesses.map(({ text }) => text).join(" "),
            {
              id: "answer",
              header: t("table-puzzle-answer"),
              cell: ({ row }) => <AnswerCell row={row} />,
              meta: { className: "col-2" },
            }
          ),
          columnHelper.accessor("status", {
            header: t("table-puzzle-status"),
            cell: ({ row, getValue }) => (
              <StatusCell row={row} value={getValue()} />
            ),
            meta: { className: "col-1" },
          }),
          columnHelper.accessor("created_on", {
            header: t("table-puzzle-created"),
            cell: ({ getValue }) => <CreationCell value={getValue()} />,
            meta: { className: "col-1" },
          }),
        ]),
      [t]
    );

    const getRowId = React.useCallback(
      (row: Puzzle, _: number, parent?: PuzzleRow) => {
        if (parent) {
          return `${parent.id}.${row.id}`;
        } else {
          return row.id.toString();
        }
      },
      []
    );

    const getSubRows = React.useCallback(
      (row: Puzzle) => (row as Puzzle & { subRows?: Puzzle[] }).subRows,
      []
    );

    const columnFilters = React.useMemo<ColumnFiltersState>(
      () => [
        { id: "status", value: filterSolved },
        { id: "tags", value: filterTags },
      ],
      [filterSolved, filterTags]
    );

    const expanded = React.useMemo(
      () => buildExpandedState(data, collapsedPuzzles),
      [data, collapsedPuzzles]
    );

    const table = useTable({
      features: puzzleTableFeatures,
      columns,
      data,
      getRowId,
      getSubRows,
      autoResetExpanded: false,
      state: {
        globalFilter: filter,
        columnFilters,
        expanded,
      },
    });

    const { rows } = table.getRowModel();
    const rowsList: React.ReactNode[] = [];
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

    const topLevelId = (row: PuzzleRow) => parseInt(row.id.split(".")[0], 10);

    rows.forEach((row, i) => {
      // Add coloring and space between top-level metas
      if (i == 0 || topLevelId(row) != topLevelId(rows[i - 1])) {
        if (i > 0) {
          rowsList.push(
            <tr key={`spacer-${row.id}`} style={{ height: "20px" }}></tr>
          );
        }

        rowsList.push(
          <tr key={`header-${row.id}`}>
            <td
              className="table-top-colorbar"
              colSpan={row.getAllCells().length + 1}
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
        <tr key={row.id} className={rowClassName(row)}>
          <td
            className="table-side-colorbar"
            style={{
              backgroundColor:
                roundColors[topLevelId(row) % roundColors.length],
            }}
          ></td>
          {row.getAllCells().map((cell) => (
            <td key={cell.id}>
              <table.FlexRender cell={cell} />
            </td>
          ))}
        </tr>
      );
    });

    return (
      <>
        <BootstrapTable size="sm">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                <th className="table-side-colorbar"></th>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className={header.column.columnDef.meta?.className}
                  >
                    {header.isPlaceholder ? null : (
                      <table.FlexRender header={header} />
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>{rowsList}</tbody>
        </BootstrapTable>
      </>
    );
  }
);
