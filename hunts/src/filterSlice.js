import { createSlice, createSelector } from "@reduxjs/toolkit";

export const SOLVE_STATE_FILTER_OPTIONS = {
  ALL: 0,
  UNSOLVED: 1, // Excludes solved feeders and everything below them.
  UNSOLVED_WITH_SOLVED_METAS: 2, // Includes unsolved feeders with solved metas.
};

export const filterSlice = createSlice({
  name: "filter",
  initialState: {
    textFilter: "",
    solveStateFilter: SOLVE_STATE_FILTER_OPTIONS.ALL,
  },
  reducers: {
    updateTextFilter: (state, action) => {
      state.textFilter = action.payload;
    },
    updateSolveStateFilter: (state, action) => {
      state.solveStateFilter = action.payload;
    },
  },
});

export const { updateTextFilter, updateSolveStateFilter } = filterSlice.actions;
export const getFilterOptions = (state) => state.filter;
export const getTextFilter = createSelector([getFilterOptions], (filter) => {
  return filter.textFilter;
});

export const getSolveStateFilter = createSelector(
  [getFilterOptions],
  (filter) => {
    return filter.solveStateFilter;
  }
);