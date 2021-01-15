import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

export const tagFilterSlice = createSlice({
  name: "tagFilter",
  initialState: {
    tags: [],
  },
  reducers: {
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

export const { toggleFilterTag } = tagFilterSlice.actions;

export default tagFilterSlice.reducer;
