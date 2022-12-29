import { createSlice } from "@reduxjs/toolkit";

// This slice is primarily used to sync changes to local storage.
export const collapsedPuzzlesSlice = createSlice({
  name: "collapsedPuzzles",
  initialState: {},
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
export const getCollapsedPuzzles = (huntId) => (state) => {
  if (!state.collapsedPuzzles.hasOwnProperty(huntId)) {
    return {};
  }
  return state.collapsedPuzzles[huntId];
};
