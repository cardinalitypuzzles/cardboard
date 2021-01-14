import { createSlice } from "@reduxjs/toolkit";
import { isRejectedAction } from "./utils";

export const tagFilterSlice = createSlice({
  name: "modal",
  initialState: {
    tagList: []
  },
  reducers: {
    toggleTagInFilter: (state, action) => {
      state.tagList = tagListWithTagToggled(state.tagList, action.payload);
    }
  }
});

function tagListWithTagToggled(tagList, tag) {
  // Returns a version of the filter tag list with the tag added
  // if the tag is not in the filter already, otherwise returns
  // a version with the tag removed.
  return tagList.map(x => x.name).includes(tag.name) ? tagList.filter(i => i.name !== tag.name) : tagList.concat([tag]);
}

export const { toggleTagInFilter } = tagFilterSlice.actions;

export default tagFilterSlice.reducer;
