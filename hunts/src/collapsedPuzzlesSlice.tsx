import { StateCreator } from "zustand";

import { RootState } from "./store";

export interface CollapsedPuzzlesSlice {
  collapsedPuzzlesSlice: {
    collapsed: Record<string, Record<string, boolean>>;

    toggleCollapsed: (huntId: string, rowId: string) => void;
    getCollapsedPuzzles: (huntId: string) => Record<string, boolean>;
  };
}

export const collapsedPuzzlesSlice: StateCreator<
  RootState,
  [["zustand/devtools", never], ["zustand/immer", never]],
  [],
  CollapsedPuzzlesSlice
> = (set, get) => ({
  collapsedPuzzlesSlice: {
    collapsed: {},

    toggleCollapsed: (huntId: string, rowId: string) => {
      set((state) => {
        if (!state.collapsedPuzzlesSlice.collapsed.hasOwnProperty(huntId)) {
          state.collapsedPuzzlesSlice.collapsed[huntId] = {};
        }
        const currentHunt = state.collapsedPuzzlesSlice.collapsed[huntId];
        currentHunt[rowId] = !currentHunt[rowId];
      });
    },
    getCollapsedPuzzles: (huntId: string) => {
      if (!get().collapsedPuzzlesSlice.collapsed.hasOwnProperty(huntId)) {
        set((state) => {
          state.collapsedPuzzlesSlice.collapsed[huntId] = {};
        });
      }

      return get().collapsedPuzzlesSlice.collapsed[huntId];
    },
  },
});

export default collapsedPuzzlesSlice;
