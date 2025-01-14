import {
  createSelector,
  createSlice,
  createAsyncThunk,
  createEntityAdapter,
} from "@reduxjs/toolkit";
import api from "./api";

import { RootState } from "./store";
import { AnswerId, HuntId, Puzzle, PuzzleId, TagId } from "./types";

export const addPuzzle = createAsyncThunk(
  "puzzles/addPuzzle",
  async ({
    huntId,
    name,
    url,
    is_meta,
    create_channels,
    assigned_meta,
  }: {
    huntId: HuntId;
    name: string;
    url: string;
    is_meta: boolean;
    create_channels: boolean;
    assigned_meta: string;
  }) => {
    const response = await api.addPuzzle(huntId, {
      name,
      url,
      is_meta,
      create_channels,
      assigned_meta,
    });
    return response;
  }
);

export const deletePuzzle = createAsyncThunk(
  "puzzles/deletePuzzle",
  async ({ huntId, id }: { huntId: HuntId; id: PuzzleId }) => {
    await api.deletePuzzle(huntId, id);
    return id;
  }
);

export const fetchPuzzles = createAsyncThunk<
  { timestamp: number; result: Puzzle[] },
  HuntId,
  { state: RootState }
>(
  "puzzles/fetchPuzzles",
  async (huntId: HuntId, { getState }: { getState: () => RootState }) => {
    const { timestamp } = getState().puzzles;
    const response = await api.getPuzzles(huntId);
    return { timestamp, result: response };
  }
);

export const updatePuzzle = createAsyncThunk(
  "puzzles/updatePuzzle",
  async ({
    huntId,
    id,
    body,
  }: {
    huntId: HuntId;
    id: PuzzleId;
    body: {
      name?: string;
      url?: string;
      is_meta?: boolean;
      create_channels?: boolean;
      status?: string;
    };
  }) => {
    const response = await api.updatePuzzle(huntId, id, body);
    return response;
  }
);

export const addAnswer = createAsyncThunk(
  "puzzles/addAnswer",
  async ({
    puzzleId,
    body,
  }: {
    puzzleId: PuzzleId;
    body: { text: string };
  }) => {
    const response = await api.addAnswer(puzzleId, body);
    return response;
  }
);

export const deleteAnswer = createAsyncThunk<
  Puzzle,
  { puzzleId: PuzzleId; answerId: AnswerId },
  { state: RootState }
>(
  "puzzles/deleteAnswer",
  async ({
    puzzleId,
    answerId,
  }: {
    puzzleId: PuzzleId;
    answerId: AnswerId;
  }) => {
    const response = await api.deleteAnswer(puzzleId, answerId);
    return response;
  }
);

export const editAnswer = createAsyncThunk(
  "puzzles/editAnswer",
  async ({
    puzzleId,
    answerId,
    body,
  }: {
    puzzleId: PuzzleId;
    answerId: AnswerId;
    body: { text: string };
  }) => {
    const response = await api.editAnswer(puzzleId, answerId, body);
    return response;
  }
);

export const editNotes = createAsyncThunk(
  "puzzles/editNotes",
  async ({
    puzzleId,
    body,
  }: {
    puzzleId: PuzzleId;
    body: { text: string };
  }) => {
    const response = await api.editNotes(puzzleId, body);
    return response;
  }
);

export const deletePuzzleTag = createAsyncThunk(
  "puzzles/deletePuzzleTag",
  async ({ puzzleId, tagId }: { puzzleId: PuzzleId; tagId: TagId }) => {
    return api.deletePuzzleTag(puzzleId, tagId);
  }
);

export const addPuzzleTag = createAsyncThunk(
  "puzzles/addPuzzleTag",
  async ({
    puzzleId,
    name,
    color,
  }: {
    puzzleId: PuzzleId;
    name: string;
    color: string;
  }) => {
    return api.addPuzzleTag(puzzleId, {
      name,
      color,
    });
  }
);

function puzzleComparator(a: Puzzle, b: Puzzle) {
  // Solved puzzles should appear below unsolved ones
  if (a.status == "SOLVED" && b.status != "SOLVED") {
    return 1;
  } else if (b.status == "SOLVED" && a.status != "SOLVED") {
    return -1;
  }
  // Feeders before metas
  if (!a.is_meta && b.is_meta) {
    return -1;
  } else if (a.is_meta && !b.is_meta) {
    return 1;
  }
  // High-priority before untagged before low-priority
  function priority(puzzle: Puzzle) {
    if (puzzle.tags.some((x) => x.is_high_pri)) {
      return 1;
    } else if (puzzle.tags.some((x) => x.is_low_pri)) {
      return -1;
    }
    return 0;
  }
  if (priority(b) != priority(a)) {
    return priority(b) - priority(a);
  }
  // Newer puzzles before old ones
  return Date.parse(b.created_on) - Date.parse(a.created_on);
}

const puzzlesAdapter = createEntityAdapter<Puzzle>();

export const puzzlesSlice = createSlice({
  name: "puzzles",
  initialState: puzzlesAdapter.getInitialState({
    timestamp: 0, // A logical timestamp for detecting stale fetchPuzzle actions
  }),
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(addPuzzle.fulfilled, (state, action) => {
        puzzlesAdapter.addOne(state, action.payload);
        ++state.timestamp;
      })
      .addCase(deletePuzzle.fulfilled, (state, action) => {
        puzzlesAdapter.removeOne(state, action.payload);
        ++state.timestamp;
      })
      .addCase(fetchPuzzles.fulfilled, (state, action) => {
        const { timestamp, result } = action.payload;
        if (timestamp == state.timestamp) {
          // Only apply the update if no other action has completed
          // in between dispatching the fetch and it completing
          puzzlesAdapter.setAll(state, result);
        }
        ++state.timestamp;
      })
      .addCase(updatePuzzle.fulfilled, (state, action) => {
        puzzlesAdapter.updateOne(state, {
          id: action.payload.id,
          changes: { ...action.payload },
        });
        ++state.timestamp;
      })
      .addCase(addAnswer.fulfilled, (state, action) => {
        puzzlesAdapter.updateOne(state, {
          id: action.payload.id,
          changes: { ...action.payload },
        });
        ++state.timestamp;
      })
      .addCase(deleteAnswer.fulfilled, (state, action) => {
        puzzlesAdapter.updateOne(state, {
          id: action.payload.id,
          changes: { ...action.payload },
        });
        ++state.timestamp;
      })
      .addCase(editAnswer.fulfilled, (state, action) => {
        puzzlesAdapter.updateOne(state, {
          id: action.payload.id,
          changes: { ...action.payload },
        });
        ++state.timestamp;
      })
      .addCase(editNotes.fulfilled, (state, action) => {
        puzzlesAdapter.updateOne(state, {
          id: action.payload.id,
          changes: { ...action.payload },
        });
        ++state.timestamp;
      })
      .addCase(deletePuzzleTag.fulfilled, (state, action) => {
        const updates = action.payload.map((updatedRecord: Puzzle) => ({
          id: updatedRecord.id,
          changes: updatedRecord,
        }));
        puzzlesAdapter.updateMany(state, updates);
        ++state.timestamp;
      })
      .addCase(addPuzzleTag.fulfilled, (state, action) => {
        const updates = action.payload.map((updatedRecord: Puzzle) => ({
          id: updatedRecord.id,
          changes: updatedRecord,
        }));
        puzzlesAdapter.updateMany(state, updates);
        ++state.timestamp;
      });
  },
});

const puzzlesSelectors = puzzlesAdapter.getSelectors(
  (state: RootState) => state.puzzles
);

export interface PuzzleTable extends Puzzle {
  subRows: Puzzle[];
}

export const selectPuzzleTableData = createSelector(
  [puzzlesSelectors.selectIds, puzzlesSelectors.selectEntities],
  (ids, entities) => {
    // We need to construct the meta/subtree relationships.
    // Each meta that contains a puzzle gets a reference to the same
    // puzzle object. Then we can offload any actual graph traversal
    // to the table library.

    // Make a deep copy of everything first
    const rowsCopy: PuzzleTable[] = ids.map((id) => ({
      ...entities[id],
      subRows: [],
    }));
    const rowMap: { [id: PuzzleId]: Puzzle } = {};
    rowsCopy.forEach((row) => {
      rowMap[row.id] = row;
    });
    // First give every meta references to all its children
    rowsCopy.forEach((row) => {
      if (row.feeders.length > 0) {
        row.subRows = [];
        row.feeders.forEach((subRowId) => {
          // This check is needed to deal with inconsistent data:
          // if we just deleted a puzzle, it may still appear as a feeder for
          // another puzzle if we haven't done a full refresh of the data yet
          if (subRowId in rowMap) {
            row.subRows.push(rowMap[subRowId]);
          }
        });
      }
    });
    // Once all the meta-child relationships are there, we can sort
    // every list of puzzles: all the subRows lists, and the list of outer puzzles as well.
    rowsCopy.forEach((row) => {
      if (row.subRows) {
        row.subRows.sort(puzzleComparator);
      }
    });
    const outerRows = rowsCopy.filter((row) => row.metas.length == 0);
    outerRows.sort(puzzleComparator);
    return outerRows;
  }
);

export const selectNumUnlocked = createSelector(
  [puzzlesSelectors.selectAll],
  (puzzles) => {
    const count = puzzles.reduce((count) => count + 1, 0);
    return count;
  }
);

export const selectNumSolved = createSelector(
  [puzzlesSelectors.selectAll],
  (puzzles) => {
    const count = puzzles.reduce(
      (count, puzzle) => (puzzle.status == "SOLVED" ? count + 1 : count),
      0
    );
    return count;
  }
);

export const selectNumUnsolved = createSelector(
  [puzzlesSelectors.selectAll],
  (puzzles) => {
    const count = puzzles.reduce(
      (count, puzzle) => (puzzle.status != "SOLVED" ? count + 1 : count),
      0
    );
    return count;
  }
);

export const selectNumMetasSolved = createSelector(
  [puzzlesSelectors.selectAll],
  (puzzles) => {
    const count = puzzles.reduce(
      (count, puzzle) =>
        puzzle.status == "SOLVED" && puzzle.is_meta ? count + 1 : count,
      0
    );
    return count;
  }
);

export const selectNumMetasUnsolved = createSelector(
  [puzzlesSelectors.selectAll],
  (puzzles) => {
    const count = puzzles.reduce(
      (count, puzzle) =>
        puzzle.status != "SOLVED" && puzzle.is_meta ? count + 1 : count,
      0
    );
    return count;
  }
);

export const selectPuzzleTags = createSelector(
  [puzzlesSelectors.selectAll],
  (puzzles) => {
    // Use a map to dedupe puzzle tags by id.
    const tagMap = new Map();
    for (const puzzle of puzzles) {
      for (const tag of puzzle.tags) {
        tagMap.set(tag.id, tag);
      }
    }
    return Array.from(tagMap.values());
  }
);

export const { selectById: selectPuzzleById } = puzzlesSelectors;

export default puzzlesSlice.reducer;
