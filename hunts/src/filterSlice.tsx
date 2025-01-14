import { createSlice, createSelector } from "@reduxjs/toolkit";
import { PuzzleTag } from "./types";
import { RootState } from "./store";

export const SOLVE_STATE_FILTER_OPTIONS = {
  ALL: 1,
  UNSOLVED: 2, // Excludes all solved puzzles and their feeders.
  UNSOLVED_WITH_SOLVED_METAS: 3, // Includes unsolved feeders with solved metas.
};

export const filterSlice = createSlice({
  name: "filter",
  initialState: {
    textFilter: "",
    solveStateFilter: SOLVE_STATE_FILTER_OPTIONS.ALL,
    tags: [] as PuzzleTag[],
  },
  reducers: {
    updateTextFilter: (state, action) => {
      state.textFilter = action.payload;
    },
    updateSolveStateFilter: (state, action) => {
      state.solveStateFilter = action.payload;
    },
    toggleFilterTag: (state, action) => {
      const newTag = action.payload;
      if (state.tags.map((tag) => tag.name).includes(newTag.name)) {
        state.tags = state.tags.filter((tag) => tag.name !== newTag.name);
      } else {
        state.tags = state.tags.concat([newTag]);
      }
    },
  },
});

export const { updateTextFilter, updateSolveStateFilter, toggleFilterTag } =
  filterSlice.actions;
export default filterSlice.reducer;
export const getFilterOptions = (state: RootState) => state.filter;
export const getTextFilter = createSelector([getFilterOptions], (filter) => {
  return filter.textFilter;
});

export const getSolveStateFilter = createSelector(
  [getFilterOptions],
  (filter) => {
    return filter.solveStateFilter;
  }
);

export const getTagFilter = createSelector([getFilterOptions], (filter) => {
  return filter.tags || [];
});
