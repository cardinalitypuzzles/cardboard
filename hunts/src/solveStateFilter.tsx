import * as React from "react";
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

  return (
    <>
      <span>{t("filter-show")}</span>
      <label>
        <input
          style={{ margin: "0 5px 0 10px" }}
          type="radio"
          checked={solveStateFilter === SOLVE_STATE_FILTER_OPTIONS.ALL}
          onChange={(evt) => {
            if (evt.target.checked) {
              setSolveStateFilter(SOLVE_STATE_FILTER_OPTIONS.ALL);
            }
          }}
        />
        {t("filter-all")}
      </label>
      <label>
        <input
          style={{ margin: "0 5px 0 10px" }}
          type="radio"
          checked={
            solveStateFilter === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED ||
            solveStateFilter ===
              SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
          }
          onChange={(evt) => {
            if (evt.target.checked) {
              setSolveStateFilter(SOLVE_STATE_FILTER_OPTIONS.UNSOLVED);
            }
          }}
        />
        {t("filter-unsolved")}
      </label>
      {(solveStateFilter === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED ||
        solveStateFilter ===
          SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS) && (
        <label>
          <input
            style={{ margin: "0 5px 0 10px" }}
            type="checkbox"
            checked={
              solveStateFilter ===
              SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
            }
            onChange={(evt) => {
              if (evt.target.checked) {
                setSolveStateFilter(
                  SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
                );
              } else {
                setSolveStateFilter(SOLVE_STATE_FILTER_OPTIONS.UNSOLVED);
              }
            }}
          />
          {t("filter-include-unsolved-with-solved-metas")}
        </label>
      )}
    </>
  );
};
