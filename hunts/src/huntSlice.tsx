import { StateCreator } from "zustand";
import { immer } from "zustand/middleware/immer"; // eslint-disable-line

import { Hunt } from "./types";
import type { RootState } from "./store";

export interface HuntSlice {
  huntSlice: {
    hunt: Hunt;
    set: (hunt: Partial<Hunt>) => void;
  };
}

export const huntSlice: StateCreator<
  RootState,
  [["zustand/devtools", never], ["zustand/immer", never]],
  [],
  HuntSlice
> = (set) => ({
  huntSlice: {
    hunt: {
      id: null,
      name: null,
      has_drive: false,
      // Caution: will be stale if you've added a tag but haven't refreshed the page.
      // TODO: keep this up to date when adding tags
      puzzle_tags: [],
      create_channel_by_default: true,
    } as Hunt,

    set: (hunt: Partial<Hunt>) => {
      set((state) => {
        state.huntSlice.hunt = {
          ...state.huntSlice.hunt,
          ...hunt,
        };
      });
    },
  },
});

export default huntSlice;
