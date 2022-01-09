import { createSlice, createSelector } from "@reduxjs/toolkit";

export const CHAT_VERSION_OPTIONS = {
  APP: 0,
  WEB: 1,
};

export const chatSlice = createSlice({
  name: "chat",
  initialState: {
    version: CHAT_VERSION_OPTIONS.APP,
  },
  reducers: {
    updateChatVersion: (state, action) => {
      state.version = action.payload;
    },
  },
});

export const { updateChatVersion } = chatSlice.actions;
export default chatSlice.reducer;
export const getChatVersion = (state) => state.chat.version;
