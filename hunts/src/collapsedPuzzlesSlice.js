import { createSlice } from "@reduxjs/toolkit";

// This slice is primarily used to sync changes to local storage.
export const collapsedPuzzlesSlice = createSlice({
  name: "collapsedPuzzles",
  initialState: {},
  reducers: {
    toggleCollapsed: (state, action) => {
      state[`${action.payload.rowId}`] = !state[`${action.payload.rowId}`];
    },
  },
});

export const { toggleCollapsed } = collapsedPuzzlesSlice.actions;
export default collapsedPuzzlesSlice.reducer;
export const getCollapsedPuzzles = (state) => state.collapsedPuzzles;
