import * as React from "react";
import { Dropdown } from "react-bootstrap";
import { useTranslation } from "react-i18next";

import { SOLVE_STATE_FILTER_OPTIONS } from "./filterSlice";
import { useStore } from "./store";
import type { PuzzleRow } from "./types";

export function filterRowsBySolveState(
  rows: PuzzleRow[],
  filterValue: SOLVE_STATE_FILTER_OPTIONS
): PuzzleRow[] {
  if (filterValue === SOLVE_STATE_FILTER_OPTIONS.ALL) {
    return rows;
  }

  if (filterValue === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED) {
    const filterUnsolved = (rowList: PuzzleRow[]): PuzzleRow[] =>
      rowList
        .filter((row) => row.original.status !== "SOLVED")
        .map((row) => ({ ...row, subRows: filterUnsolved(row.subRows) }));
    return filterUnsolved(rows);
  }

  if (filterValue === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS) {
    const filterWithSolvedMetas = (rowList: PuzzleRow[]): PuzzleRow[] => {
      const result: PuzzleRow[] = [];
      for (const row of rowList) {
        const filteredSubRows = filterWithSolvedMetas(row.subRows);
        if (row.original.status !== "SOLVED" || filteredSubRows.length > 0) {
          result.push({ ...row, subRows: filteredSubRows });
        }
      }
      return result;
    };
    return filterWithSolvedMetas(rows);
  }

  return rows;
}

export const SolvedStateFilter = () => {
  const { solveStateFilter, setSolveStateFilter } = useStore(
    (store) => store.filterSlice
  );
  const { t } = useTranslation();

  const OPTIONS = [
    {
      value: SOLVE_STATE_FILTER_OPTIONS.ALL,
      labelKey: "filter-all",
    },
    {
      value: SOLVE_STATE_FILTER_OPTIONS.UNSOLVED,
      labelKey: "filter-unsolved",
    },
    {
      value: SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS,
      labelKey: "filter-unsolved-plus",
    },
  ];
  const currentLabelKey =
    OPTIONS.find((o) => o.value === solveStateFilter)?.labelKey ?? "filter-all";

  return (
    <Dropdown
      onSelect={(key: string | null) => {
        if (key !== null) {
          setSolveStateFilter(Number(key));
        }
      }}
    >
      <Dropdown.Toggle as="button" className="cb-filter-dd-toggle">
        {t("filter-show")} {t(currentLabelKey)}
      </Dropdown.Toggle>
      <Dropdown.Menu>
        {OPTIONS.map((option) => (
          <Dropdown.Item
            eventKey={String(option.value)}
            key={option.value}
            active={solveStateFilter === option.value}
          >
            {t(option.labelKey)}
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
};
