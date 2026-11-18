import { StateCreator } from "zustand";

import api from "./api";
import { RootState } from "./store";
import { AnswerId, Puzzle, PuzzleId, PuzzleTag, TagId } from "./types";

export interface PuzzlesSlice {
  puzzlesSlice: {
    lastUpdate: number;
    puzzles: { [id: PuzzleId]: Puzzle };

    getPuzzle: (id: PuzzleId) => Puzzle;
    allPuzzles: (filterFn?: (p: Puzzle) => boolean) => Puzzle[];
    fetchAllPuzzles: () => Promise<void>;
    updatePuzzleFromDict: (response: Record<string, any>) => void;
    bulkUpdatePuzzlesFromDict: (response: Record<string, any>[]) => void;

    addPuzzle: (args: Record<string, any>) => Promise<void>;
    deletePuzzle: (id: PuzzleId) => Promise<void>;
    updatePuzzle: (
      id: PuzzleId,
      changes: Partial<Puzzle> | { create_channels: boolean }
    ) => Promise<void>;
    addAnswer: (id: PuzzleId, text: string) => Promise<void>;
    deleteAnswer: (id: PuzzleId, answerId: AnswerId) => Promise<void>;
    editAnswer: (
      id: PuzzleId,
      answerId: AnswerId,
      text: string
    ) => Promise<void>;
    addPuzzleTag: (
      puzzleId: PuzzleId,
      tag: { name: string; color: string }
    ) => Promise<void>;
    deletePuzzleTag: (puzzleId: PuzzleId, tagId: TagId) => Promise<void>;
    editNotes: (puzzleId: PuzzleId, text: string) => Promise<void>;

    numPuzzlesUnlocked: () => number;
    numPuzzlesSolved: () => number;
    numMetasUnlocked: () => number;
    numMetasSolved: () => number;

    allPuzzleTags: () => PuzzleTag[];
  };
}

export const puzzlesSlice: StateCreator<
  RootState,
  [["zustand/devtools", never], ["zustand/immer", never]],
  [],
  PuzzlesSlice
> = (set, get) => ({
  puzzlesSlice: {
    lastUpdate: 0, // A logical timestamp for detecting stale fetchPuzzle actions
    puzzles: {} as { [id: PuzzleId]: Puzzle },

    getPuzzle(id: PuzzleId) {
      return get().puzzlesSlice.puzzles[id];
    },
    allPuzzles(filterFn?: (p: Puzzle) => boolean) {
      return Object.values<Puzzle>(get().puzzlesSlice.puzzles).filter(
        filterFn ?? (() => true)
      );
    },
    fetchAllPuzzles: async () => {
      let huntId = get().huntSlice.hunt.id;
      if (huntId === null) {
        return;
      }

      return api.getPuzzles(huntId).then((response) => {
        get().puzzlesSlice.bulkUpdatePuzzlesFromDict(response);
      });
    },

    updatePuzzleFromDict: (response: Record<string, any>) => {
      set((state) => {
        state.puzzlesSlice.lastUpdate = Date.now();
        state.puzzlesSlice.puzzles[response.id] = {
          ...state.puzzlesSlice.puzzles[response.id],
          ...response,
        };
      });
    },
    bulkUpdatePuzzlesFromDict: (response: Record<string, any>[]) => {
      set((state) => {
        state.puzzlesSlice.lastUpdate = Date.now();
        for (const p of response) {
          state.puzzlesSlice.puzzles[p.id] = {
            ...state.puzzlesSlice.puzzles[p.id],
            ...p,
          };
        }
      });
    },

    addPuzzle: async (args: Record<string, any>) => {
      return api
        .addPuzzle(get().huntSlice.hunt.id!, {
          name: args.name,
          url: args.url,
          is_meta: args.is_meta,
          create_channels: args.create_channels,
          assigned_meta: args.assigned_meta,
        })
        .then((response) => {
          set((state) => {
            let p = response;
            state.puzzlesSlice.lastUpdate = Date.now();
            state.puzzlesSlice.puzzles[p.id] = p;
          });
        });
    },
    deletePuzzle: async (id: PuzzleId) => {
      return api.deletePuzzle(get().huntSlice.hunt.id!, id).then((response) => {
        set((state) => {
          state.puzzlesSlice.lastUpdate = Date.now();
          delete state.puzzlesSlice.puzzles[response.id];
        });
      });
    },
    updatePuzzle: async (
      id: PuzzleId,
      changes: Partial<Puzzle> | { create_channels: boolean }
    ) => {
      return api
        .updatePuzzle(get().huntSlice.hunt.id!, id, changes)
        .then((response) => {
          get().puzzlesSlice.updatePuzzleFromDict(response);
        });
    },
    addAnswer: async (id: PuzzleId, text: string) => {
      return api.addAnswer(id, { text }).then((response) => {
        get().puzzlesSlice.updatePuzzleFromDict(response);
      });
    },
    deleteAnswer: async (id: PuzzleId, answerId: AnswerId) => {
      return api.deleteAnswer(id, answerId).then((response) => {
        get().puzzlesSlice.updatePuzzleFromDict(response);
      });
    },
    editAnswer: async (id: PuzzleId, answerId: AnswerId, text: string) => {
      return api.editAnswer(id, answerId, { text }).then((response) => {
        get().puzzlesSlice.updatePuzzleFromDict(response);
      });
    },
    addPuzzleTag: async (
      puzzleId: PuzzleId,
      tag: { name: string; color: string }
    ) => {
      return api.addPuzzleTag(puzzleId, tag).then((response) => {
        get().puzzlesSlice.bulkUpdatePuzzlesFromDict(response);
      });
    },
    deletePuzzleTag: async (puzzleId: PuzzleId, tagId: TagId) => {
      return api.deletePuzzleTag(puzzleId, tagId).then((response) => {
        get().puzzlesSlice.bulkUpdatePuzzlesFromDict(response);
      });
    },
    editNotes: async (puzzleId: PuzzleId, text: string) => {
      return api.editNotes(puzzleId, { text }).then((response) => {
        set((state) => {
          state.puzzlesSlice.puzzles[puzzleId].notes = response["notes"];
        });
      });
    },

    numPuzzlesUnlocked: () => {
      return Object.values<Puzzle>(get().puzzlesSlice.puzzles).length;
    },
    numPuzzlesSolved: () => {
      return Object.values<Puzzle>(get().puzzlesSlice.puzzles).filter(
        (p) => p.status == "SOLVED"
      ).length;
    },
    numMetasUnlocked: () => {
      return Object.values<Puzzle>(get().puzzlesSlice.puzzles).filter(
        (p) => p.is_meta
      ).length;
    },
    numMetasSolved: () => {
      return Object.values<Puzzle>(get().puzzlesSlice.puzzles).filter(
        (p) => p.status == "SOLVED" && p.is_meta
      ).length;
    },

    allPuzzleTags: () => {
      const tags = new Map();
      for (const puzzle of Object.values<Puzzle>(get().puzzlesSlice.puzzles)) {
        for (const tag of puzzle.tags) {
          tags.set(tag.id, tag);
        }
      }
      return Array.from(tags.values());
    },
  },
});

export default puzzlesSlice;
