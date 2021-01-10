import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "./api";

export const fetchHunt = createAsyncThunk("hunt/fetchHunt", async (huntId) => {
  const response = await api.getHunt(huntId);
  return response;
});

export const huntSlice = createSlice({
  name: "hunt",
  initialState: {
    id: null,
    name: null,
    num_solved: 0,
    num_unsolved: 0,
    num_unlocked: 0,
    num_metas_solved: 0,
  },
  reducers: {},
  extraReducers: {
    [fetchHunt.fulfilled]: (state, action) => {
      state.id = action.payload.id;
      state.name = action.payload.name;
      state.num_solved = action.payload.num_solved;
      state.num_unsolved = action.payload.num_unsolved;
      state.num_unlocked = action.payload.num_unlocked;
      state.num_metas_solved = action.payload.num_metas_solved;
    },
  },
});

export const { reducers } = huntSlice.actions;

export default huntSlice.reducer;
