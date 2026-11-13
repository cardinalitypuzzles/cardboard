import { StateCreator } from "zustand";
import { immer } from "zustand/middleware/immer"; // eslint-disable-line

import { Hunt, PuzzleTag, TagId } from "./types";
import type { RootState } from "./store";

export interface HuntSlice {
  huntSlice: {
    hunt: Hunt;
    set: (hunt: Partial<Hunt>) => void;
    upsertTag: (tag: PuzzleTag) => void;
    removeTag: (tagId: TagId) => void;
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
      slug: null,
      has_drive: false,
      is_admin: false,
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

    upsertTag: (tag: PuzzleTag) => {
      set((state) => {
        const idx = state.huntSlice.hunt.puzzle_tags.findIndex(
          (t) => t.id === tag.id
        );
        if (idx >= 0) {
          state.huntSlice.hunt.puzzle_tags[idx] = tag;
        } else {
          state.huntSlice.hunt.puzzle_tags.push(tag);
        }
      });
    },

    removeTag: (tagId: TagId) => {
      set((state) => {
        state.huntSlice.hunt.puzzle_tags =
          state.huntSlice.hunt.puzzle_tags.filter((t) => t.id !== tagId);
      });
    },
  },
});

export default huntSlice;
