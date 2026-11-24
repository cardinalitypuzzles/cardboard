import React from "react";
import { useTranslation } from "react-i18next";
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
import type { PuzzleRow, PuzzleTableData, PuzzleTag } from "./types";

// Unassigned puzzles (top-level rows that are not metas) form one continuous
// visual block instead of one group per puzzle. Nested feeder rows inherit
// their top-level ancestor's group key so they keep the ancestor's palette.
function topLevelGroupKey(item: PuzzleTableData): string {
  return item.is_meta ? `meta:${item.id}` : "unassigned";
}

function buildPuzzleTree(data: PuzzleTableData[]): {
  rows: PuzzleRow[];
  flatRows: PuzzleRow[];
} {
  const flatRows: PuzzleRow[] = [];

  const _dfsBuild = (
    items: PuzzleTableData[],
    depth: number,
    parentId?: string,
    groupKey?: string
  ): PuzzleRow[] =>
    items.map((item) => {
      const id = parentId ? `${parentId}.${item.id}` : item.id.toString();
      const key =
        depth === 0 ? topLevelGroupKey(item) : (groupKey as string);
      const row: PuzzleRow = {
        id,
        parentId,
        depth,
        original: item,
        subRows: [],
        groupKey: key,
      };
      flatRows.push(row);
      if (item.subRows.length > 0) {
        row.subRows = _dfsBuild(item.subRows, depth + 1, id, key);
      }
      return row;
    });

  return {
    rows: _dfsBuild(data, 0),
    flatRows,
  };
}

function flattenRows(rows: PuzzleRow[], out: PuzzleRow[] = []): PuzzleRow[] {
  for (const row of rows) {
    out.push(row);
    if (row.subRows.length > 0) {
      flattenRows(row.subRows, out);
    }
  }
  return out;
}

function filterPuzzleRows(
  rows: PuzzleRow[],
  solveState: SOLVE_STATE_FILTER_OPTIONS,
  filterTags: PuzzleTag[],
  globalFilter: string
): PuzzleRow[] {
  let filteredRows = filterRowsBySolveState(rows, solveState);

  if (filterTags.length > 0 || globalFilter) {
    let candidateFlatRows = flattenRows(filteredRows);

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
        (row: PuzzleRow) => row.original.name,
        (row: PuzzleRow) => row.original.tags.map(({ name }) => name).join(" "),
        (row: PuzzleRow) => row.original.status,
        (row: PuzzleRow) =>
          row.original.guesses.map(({ text }) => text).join(" "),
      ];
      candidateFlatRows = words.reduceRight(
        (results, word) => matchSorter(results, word, { keys }),
        candidateFlatRows
      );
    }

    const matchedIds = new Set(candidateFlatRows.map((row) => row.id));
    const _filter = (rowList: PuzzleRow[]): PuzzleRow[] => {
      const result: PuzzleRow[] = [];
      for (const row of rowList) {
        const matchedSubRows = _filter(row.subRows);
        if (matchedIds.has(row.id)) {
          result.push({ ...row, subRows: matchedSubRows });
        } else {
          result.push(...matchedSubRows);
        }
      }
      return result;
    };
    filteredRows = _filter(filteredRows);
  }

  return filteredRows;
}

function expandPuzzleRows(
  rows: PuzzleRow[],
  collapsedPuzzles: Record<string, boolean>
): PuzzleRow[] {
  const expanded: PuzzleRow[] = [];
  const walk = (rowList: PuzzleRow[]) => {
    for (const row of rowList) {
      expanded.push(row);
      if (row.subRows.length > 0 && !collapsedPuzzles[row.id]) {
        walk(row.subRows);
      }
    }
  };
  walk(rows);
  return expanded;
}

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

const MetaGroupHeaderRows = React.memo(
  ({
    hasSpacerSlot,
    showSpacer,
    showHeader,
    colSpan,
    color,
  }: {
    hasSpacerSlot: boolean;
    showSpacer: boolean;
    showHeader: boolean;
    colSpan: number;
    color: string;
  }) => (
    <>
      {hasSpacerSlot && (
        <tr hidden={!showSpacer} className="table-group-spacer"></tr>
      )}
      <tr hidden={!showHeader}>
        <td
          className="table-top-colorbar"
          colSpan={colSpan}
          style={{
            background: `linear-gradient(90deg, ${color}, transparent)`,
          }}
        ></td>
      </tr>
    </>
  )
);

const PuzzleTableRowCells = React.memo(
  ({ row, color }: { row: PuzzleRow; color: string; language: string }) => (
    <>
      <td
        className="table-side-colorbar"
        style={{
          backgroundColor: color,
        }}
      ></td>
      <td>
        <NameCell row={row} value={row.original.name} />
      </td>
      <td>
        <LinkCell row={row} />
      </td>
      <td>
        <TagCell row={row} />
      </td>
      <td>
        <NotesCell row={row} value={row.original.notes} />
      </td>
      <td>
        <UsersCell row={row} />
      </td>
      <td>
        <AnswerCell row={row} />
      </td>
      <td>
        <StatusCell row={row} value={row.original.status} />
      </td>
      <td>
        <CreationCell value={row.original.created_on} />
      </td>
    </>
  )
);

const PuzzleTableRow = React.memo(
  ({
    row,
    isHidden,
    color,
    language,
  }: {
    row: PuzzleRow;
    isHidden: boolean;
    color: string;
    language: string;
  }) => (
    <tr hidden={isHidden} className={rowClassName(row)}>
      <PuzzleTableRowCells row={row} color={color} language={language} />
    </tr>
  )
);

const ROUND_COLORS = [
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

// Neutral side-rail color for unassigned puzzles: the round palette is
// reserved for meta groups. Defined as a CSS var so it flips with dark mode.
const UNASSIGNED_RAIL_COLOR = "var(--cb-unassigned-rail)";

const isMetaGroupKey = (groupKey: string) => groupKey.startsWith("meta:");

// One spacer row for an unassigned run; no colorbar/header. Rendered hidden
// when the run should not be separated from what precedes it.
const UnassignedSpacerRow = React.memo(({ hidden }: { hidden: boolean }) => (
  <tr hidden={hidden} className="table-group-spacer"></tr>
));

export const PuzzleTable = React.memo(
  ({
    data,
    filterSolved,
    filterTags,
  }: {
    data: PuzzleTableData[];
    filterSolved: number;
    filterTags: PuzzleTag[];
  }) => {
    const { t, i18n } = useTranslation();
    const filter = useStore((state) => state.filterSlice.filterValue);
    const collapsedPuzzles = useStore((state) =>
      state.collapsedPuzzlesSlice.getCollapsedPuzzles(
        CURRENT_HUNT_ID.toString()
      )
    );

    const tree = React.useMemo(() => buildPuzzleTree(data), [data]);

    const filteredRows = React.useMemo(
      () =>
        filterPuzzleRows(
          tree.rows,
          filterSolved as SOLVE_STATE_FILTER_OPTIONS,
          filterTags,
          filter
        ),
      [tree.rows, filterSolved, filterTags, filter]
    );

    const visibleRows = React.useMemo(
      () => expandPuzzleRows(filteredRows, collapsedPuzzles),
      [filteredRows, collapsedPuzzles]
    );

    const visibleRowIds = new Set(visibleRows.map((row) => row.id));
    const visibleGroupKeys = new Set(visibleRows.map((row) => row.groupKey));

    const headerColSpan = 9;
    const language = i18n.resolvedLanguage || "en";
    const rowsList: React.ReactNode[] = [];
    let seenVisibleGroup = false;
    let lastVisibleGroupWasMeta = false;
    let prevGroupKey: string | null = null;

    tree.flatRows.forEach((row, i) => {
      const groupKey = row.groupKey;
      const isMetaGroup = isMetaGroupKey(groupKey);
      const color = isMetaGroup
        ? ROUND_COLORS[
            parseInt(groupKey.slice("meta:".length), 10) %
              ROUND_COLORS.length
          ]
        : UNASSIGNED_RAIL_COLOR;

      if (i == 0 || groupKey != prevGroupKey) {
        const showHeader = visibleGroupKeys.has(groupKey);
        if (isMetaGroup) {
          const showSpacer = showHeader && seenVisibleGroup;
          if (showHeader) {
            seenVisibleGroup = true;
            lastVisibleGroupWasMeta = true;
          }
          rowsList.push(
            <MetaGroupHeaderRows
              key={`group-header-${groupKey}`}
              hasSpacerSlot={i > 0}
              showSpacer={showSpacer}
              showHeader={showHeader}
              colSpan={headerColSpan}
              color={color}
            />
          );
        } else {
          // Unassigned puzzles are one continuous block: only separate the
          // run from metas above it. Never a colorbar or heading.
          const showSpacer =
            showHeader && seenVisibleGroup && lastVisibleGroupWasMeta;
          if (showHeader) {
            seenVisibleGroup = true;
            lastVisibleGroupWasMeta = false;
          }
          if (i > 0) {
            rowsList.push(
              <UnassignedSpacerRow
                key={`group-spacer-${groupKey}-${row.id}`}
                hidden={!showSpacer}
              />
            );
          }
        }
        prevGroupKey = groupKey;
      }

      rowsList.push(
        <PuzzleTableRow
          key={row.id}
          row={row}
          isHidden={!visibleRowIds.has(row.id)}
          color={color}
          language={language}
        />
      );
    });

    return (
      <BootstrapTable size="sm">
        <thead>
          <tr>
            <th className="table-side-colorbar"></th>
            <th className="col-2">{t("table-puzzle-name")}</th>
            <th className="col-1">{t("table-puzzle-links")}</th>
            <th className="col-2">{t("table-puzzle-tags")}</th>
            <th className="col-2">{t("table-puzzle-notes")}</th>
            <th></th>
            <th className="col-2">{t("table-puzzle-answer")}</th>
            <th className="col-1">{t("table-puzzle-status")}</th>
            <th className="col-1">{t("table-puzzle-created")}</th>
          </tr>
        </thead>
        <tbody>{rowsList}</tbody>
      </BootstrapTable>
    );
  }
);
