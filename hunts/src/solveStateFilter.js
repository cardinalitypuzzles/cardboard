import * as React from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  getSolveStateFilter,
  SOLVE_STATE_FILTER_OPTIONS,
  updateSolveStateFilter,
} from "./filterSlice";

function isUnsolved(tableRow) {
  return tableRow.values.status !== "SOLVED";
}

function isSolved(tableRow) {
  return !isUnsolved(tableRow);
}

function getDescendants(tableRow) {
  const allChildren = [tableRow];
  for (let i = 0; i < allChildren.length; i++) {
    const current = allChildren[i];
    Array.prototype.push.apply(allChildren, current.subRows);
  }
  return allChildren;
}

function hasUnsolvedDescendants(tableRow) {
  return getDescendants(tableRow).filter(isUnsolved).length !== 0;
}

export function filterSolvedPuzzlesfn(rows, id, filterValue) {
  if (filterValue === SOLVE_STATE_FILTER_OPTIONS.ALL) {
    return rows;
  }

  if (filterValue === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED) {
    const rowIdsToExclude = new Set();
    rows.forEach((row) => {
      if (isSolved(row)) {
        // Explicitly exclude this row.
        rowIdsToExclude.add(row.id);
        // Also exclude its children.
        getDescendants(row).forEach((subRow) => {
          rowIdsToExclude.add(subRow.id);
        });
      }
    });
    return rows
      .filter((row) => !rowIdsToExclude.has(row.id))
      .map((row) => Object.assign({}, row));
  }

  if (filterValue === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS) {
    return rows
      .filter((row) => {
        return isUnsolved(row) || hasUnsolvedDescendants(row);
      })
      .map((row) => Object.assign({}, row));
  }
}

// If the value is empty, it should be treated as equivalent to a no-op and be removed.
filterSolvedPuzzlesfn.autoRemove = (val) => !val;

export const SolvedStateFilter = () => {
  const filterSolved = useSelector(getSolveStateFilter);
  const dispatch = useDispatch();
  return (
    <>
      <span>Show:</span>
      <label>
        <input
          style={{ margin: "0 5px 0 10px" }}
          type="radio"
          checked={filterSolved === SOLVE_STATE_FILTER_OPTIONS.ALL}
          onChange={(evt) => {
            if (evt.target.checked) {
              dispatch(updateSolveStateFilter(SOLVE_STATE_FILTER_OPTIONS.ALL));
            }
          }}
        ></input>
        All
      </label>
      <label>
        <input
          style={{ margin: "0 5px 0 10px" }}
          type="radio"
          checked={
            filterSolved === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED ||
            filterSolved ===
              SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
          }
          onChange={(evt) => {
            if (evt.target.checked) {
              dispatch(
                updateSolveStateFilter(SOLVE_STATE_FILTER_OPTIONS.UNSOLVED)
              );
            }
          }}
        ></input>
        Unsolved
      </label>
      {(filterSolved === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED ||
        filterSolved ===
          SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS) && (
        <label>
          <input
            style={{ margin: "0 5px 0 10px" }}
            type="checkbox"
            checked={
              filterSolved ===
              SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
            }
            onChange={(evt) => {
              if (evt.target.checked) {
                dispatch(
                  updateSolveStateFilter(
                    SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
                  )
                );
              } else {
                dispatch(
                  updateSolveStateFilter(SOLVE_STATE_FILTER_OPTIONS.UNSOLVED)
                );
              }
            }}
          ></input>
          Include unsolved w/ solved metas
        </label>
      )}
    </>
  );
};
