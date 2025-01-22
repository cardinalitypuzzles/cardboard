import { StateCreator } from "zustand";

import { RootState } from "./store";

export enum CHAT_VERSION_OPTIONS {
  APP = 1,
  WEB = 2,
}

export interface ChatSlice {
  chatSlice: {
    version: CHAT_VERSION_OPTIONS;

    updateChatVersion: (version: CHAT_VERSION_OPTIONS) => void;
  };
}

export const chatSlice: StateCreator<
  RootState,
  [["zustand/devtools", never], ["zustand/immer", never]],
  [],
  ChatSlice
> = (set, get) => ({
  chatSlice: {
    version: CHAT_VERSION_OPTIONS.APP,
    updateChatVersion: (version: CHAT_VERSION_OPTIONS) => {
      set((state) => {
        state.chatSlice.version = version;
      });
    },
  },
});

export default chatSlice;
