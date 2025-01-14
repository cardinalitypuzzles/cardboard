import { createSlice } from "@reduxjs/toolkit";
import { RootState } from "./store";

// This slice is primarily used to sync changes to local storage.
export const collapsedPuzzlesSlice = createSlice({
  name: "collapsedPuzzles",
  initialState: {} as Record<string, Record<string, boolean>>,
  reducers: {
    toggleCollapsed: (state, action) => {
      if (!state.hasOwnProperty(action.payload.huntId)) {
        state[action.payload.huntId] = {};
      }
      const currentHunt = state[action.payload.huntId];
      currentHunt[action.payload.rowId] = !currentHunt[action.payload.rowId];
    },
  },
});

export const { toggleCollapsed } = collapsedPuzzlesSlice.actions;
export default collapsedPuzzlesSlice.reducer;
export const getCollapsedPuzzles = (huntId: string) => (state: RootState) => {
  if (!state.collapsedPuzzles.hasOwnProperty(huntId)) {
    return {};
  }
  return state.collapsedPuzzles[huntId];
};
