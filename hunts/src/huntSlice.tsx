import {
  createSlice,
  createAsyncThunk,
  createSelector,
} from "@reduxjs/toolkit";
import api from "./api";

import { Hunt, HuntId } from "./types";
import { RootState } from "./store";

export const fetchHunt = createAsyncThunk(
  "hunt/fetchHunt",
  async (huntId: HuntId) => {
    const response = await api.getHunt(huntId);
    return response;
  }
);

export const huntSlice = createSlice({
  name: "hunt",
  initialState: {
    id: null,
    name: null,
    has_drive: false,
    puzzle_tags: [],
    create_channel_by_default: true,
  } as Hunt,
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

export default huntSlice.reducer;

const selectHunt = (state: RootState) => state.hunt;

export const selectHuntId = createSelector([selectHunt], (hunt) => hunt.id);
export const selectHuntTags = createSelector(
  [selectHunt],
  (hunt) => hunt.puzzle_tags
);
export const selectHuntCreateChannelByDefault = createSelector(
  [selectHunt],
  (hunt) => hunt.create_channel_by_default
);
