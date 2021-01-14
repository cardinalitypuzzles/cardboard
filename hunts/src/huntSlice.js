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
    has_drive: false,
  },
  reducers: {},
  extraReducers: {
    [fetchHunt.fulfilled]: (state, action) => {
      state.id = action.payload.id;
      state.name = action.payload.name;
      state.has_drive = action.payload.has_drive;
    },
  },
});

export const { reducers } = huntSlice.actions;

export default huntSlice.reducer;
