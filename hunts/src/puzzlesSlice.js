import {
  createSelector,
  createSlice,
  createAsyncThunk,
  createEntityAdapter,
} from "@reduxjs/toolkit";
import api from "./api";

export const addPuzzle = createAsyncThunk(
  "puzzles/addPuzzle",
  async ({ huntId, name, url, is_meta }) => {
    const response = await api.addPuzzle(huntId, { name, url, is_meta });
    return response;
  }
);

export const deletePuzzle = createAsyncThunk(
  "puzzles/deletePuzzle",
  async ({ huntId, id }) => {
    await api.deletePuzzle(huntId, id);
    return id;
  }
);

export const fetchPuzzles = createAsyncThunk(
  "puzzles/fetchPuzzles",
  async (huntId, { getState }) => {
    const { timestamp } = getState().puzzles;
    const response = await api.getPuzzles(huntId);
    response.forEach((puzzle) => {
      puzzle.recent_editors = [
        "Peter Vera",
        "Shuxin Zhan",
        "Ryan Gossiaux",
        "Ryan Liu",
        "Anthony Hsu",
        "Max Chang",
        "Benji Nguyen",
        "Ali Chang",
        "Akira Baruah",
      ].filter((v, idx) => {
        if (puzzle.id === 9) {
          return false;
        }
        return idx < puzzle.id;
      });
    });
    return { timestamp, result: response };
  }
);

export const updatePuzzle = createAsyncThunk(
  "puzzles/updatePuzzle",
  async ({ huntId, id, body }) => {
    const response = await api.updatePuzzle(huntId, id, body);
    return response;
  }
);

export const addAnswer = createAsyncThunk(
  "puzzles/addAnswer",
  async ({ puzzleId, body }) => {
    const response = await api.addAnswer(puzzleId, body);
    return response;
  }
);

export const deleteAnswer = createAsyncThunk(
  "puzzles/deleteAnswer",
  async ({ puzzleId, answerId }) => {
    const response = await api.deleteAnswer(puzzleId, answerId);
    return response;
  }
);

export const editAnswer = createAsyncThunk(
  "puzzles/editAnswer",
  async ({ puzzleId, answerId, body }) => {
    const response = await api.editAnswer(puzzleId, answerId, body);
    return response;
  }
);

export const deletePuzzleTag = createAsyncThunk(
  "puzzles/deletePuzzleTag",
  async ({ puzzleId, tagId }) => {
    return api.deletePuzzleTag(puzzleId, tagId);
  }
);

export const addPuzzleTag = createAsyncThunk(
  "puzzles/addPuzzleTag",
  async ({ puzzleId, name, color }) => {
    return api.addPuzzleTag(puzzleId, {
      name,
      color,
    });
  }
);

function puzzleComparator(a, b) {
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
  function priority(row) {
    if (row.tags.some((x) => x.is_high_pri)) {
      return 1;
    } else if (row.tags.some((x) => x.is_low_pri)) {
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

const puzzlesAdapter = createEntityAdapter();

export const puzzlesSlice = createSlice({
  name: "puzzles",
  initialState: puzzlesAdapter.getInitialState({
    timestamp: 0, // A logical timestamp for detecting stale fetchPuzzle actions
  }),
  reducers: {},
  extraReducers: {
    [addPuzzle.fulfilled]: (state, action) => {
      puzzlesAdapter.addOne(state, action.payload);
      ++state.timestamp;
    },
    [deletePuzzle.fulfilled]: (state, action) => {
      puzzlesAdapter.removeOne(state, action.payload);
      ++state.timestamp;
    },
    [fetchPuzzles.fulfilled]: (state, action) => {
      const { timestamp, result } = action.payload;
      if (timestamp == state.timestamp) {
        // Only apply the update if no other action has completed
        // in between dispatching the fetch and it completing
        puzzlesAdapter.setAll(state, result);
      }
      ++state.timestamp;
    },
    [updatePuzzle.fulfilled]: (state, action) => {
      puzzlesAdapter.updateOne(state, {
        id: action.payload.id,
        changes: { ...action.payload },
      });
      ++state.timestamp;
    },
    [addAnswer.fulfilled]: (state, action) => {
      puzzlesAdapter.updateOne(state, {
        id: action.payload.id,
        changes: { ...action.payload },
      });
      ++state.timestamp;
    },
    [deleteAnswer.fulfilled]: (state, action) => {
      puzzlesAdapter.updateOne(state, {
        id: action.payload.id,
        changes: { ...action.payload },
      });
      ++state.timestamp;
    },
    [editAnswer.fulfilled]: (state, action) => {
      puzzlesAdapter.updateOne(state, {
        id: action.payload.id,
        changes: { ...action.payload },
      });
      ++state.timestamp;
    },
    [deletePuzzleTag.fulfilled]: (state, action) => {
      const updates = action.payload.map((updatedRecord) => ({
        id: updatedRecord.id,
        changes: updatedRecord,
      }));
      puzzlesAdapter.updateMany(state, updates);
      ++state.timestamp;
    },
    [addPuzzleTag.fulfilled]: (state, action) => {
      const updates = action.payload.map((updatedRecord) => ({
        id: updatedRecord.id,
        changes: updatedRecord,
      }));
      puzzlesAdapter.updateMany(state, updates);
      ++state.timestamp;
    },
  },
});

const puzzlesSelectors = puzzlesAdapter.getSelectors((state) => state.puzzles);

export const selectPuzzleTableData = createSelector(
  [puzzlesSelectors.selectIds, puzzlesSelectors.selectEntities],
  (ids, entities) => {
    // We need to construct the meta/subtree relationships.
    // Each meta that contains a puzzle gets a reference to the same
    // puzzle object. Then we can offload any actual graph traversal
    // to the table library.

    // Make a deep copy of everything first
    const rowsCopy = ids.map((id) => ({ ...entities[id] }));
    const rowMap = {};
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

export const { selectById: selectPuzzleById } = puzzlesSelectors;
export const { reducers } = puzzlesSlice.actions;

export default puzzlesSlice.reducer;
