import { StateCreator } from "zustand";
import { immer } from "zustand/middleware/immer"; // eslint-disable-line

import { PuzzleTag } from "./types";
import { RootState } from "./store";

export enum SOLVE_STATE_FILTER_OPTIONS {
  ALL = 1,
  UNSOLVED = 2, // Excludes all solved puzzles and their feeders.
  UNSOLVED_WITH_SOLVED_METAS = 3, // Includes unsolved feeders with solved metas.
}

export interface FilterSlice {
  filterSlice: {
    filterValue: string;
    solveStateFilter: SOLVE_STATE_FILTER_OPTIONS;
    tags: PuzzleTag[];

    updateFilterValue: (filterValue: string) => void;
    updateSolveStateFilter: (
      solveStateFilter: SOLVE_STATE_FILTER_OPTIONS
    ) => void;
    toggleFilterTag: (newTag: PuzzleTag) => void;
  };
}

export const filterSlice: StateCreator<
  RootState,
  [["zustand/devtools", never], ["zustand/immer", never]],
  [],
  FilterSlice
> = (set, get) => ({
  filterSlice: {
    filterValue: "",
    solveStateFilter: SOLVE_STATE_FILTER_OPTIONS.ALL,
    tags: [] as PuzzleTag[],

    updateFilterValue: (filterValue: string) => {
      set((state) => {
        state.filterSlice.filterValue = filterValue;
      });
    },
    updateSolveStateFilter: (solveStateFilter: SOLVE_STATE_FILTER_OPTIONS) => {
      set((state) => ({
        filterSlice: { ...state.filterSlice, solveStateFilter },
      }));
    },
    toggleFilterTag: (newTag: PuzzleTag) => {
      set((state) => {
        if (
          state.filterSlice.tags
            .map((tag: PuzzleTag) => tag.name)
            .includes(newTag.name)
        ) {
          state.filterSlice.tags = state.filterSlice.tags.filter(
            (tag: PuzzleTag) => tag.name !== newTag.name
          );
          return;
        }

        state.filterSlice.tags = state.filterSlice.tags.concat([newTag]);
      });
    },
  },
});

export default filterSlice;
