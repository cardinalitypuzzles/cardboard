import {
  createSlice,
  createAsyncThunk,
  createSelector,
} from "@reduxjs/toolkit";
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
    puzzle_tags: [],
    create_channel_by_default: true,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchHunt.fulfilled, (state, action) => {
      state.id = action.payload.id;
      state.name = action.payload.name;
      state.has_drive = action.payload.has_drive;
      state.puzzle_tags = action.payload.puzzle_tags;
      state.create_channel_by_default =
        action.payload.create_channel_by_default;
    });
  },
});

export const { reducers } = huntSlice.actions;

export default huntSlice.reducer;

const selectHunt = (state) => state.hunt;

export const selectHuntId = createSelector([selectHunt], (hunt) => hunt.id);
export const selectHuntTags = createSelector(
  [selectHunt],
  (hunt) => hunt.puzzle_tags
);
export const selectHuntCreateChannelByDefault = createSelector(
  [selectHunt],
  (hunt) => hunt.create_channel_by_default
);
