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
    const response = await api.deletePuzzle(huntId, id);
    return id;
  }
);

export const fetchPuzzles = createAsyncThunk(
  "puzzles/fetchPuzzles",
  async (huntId) => {
    const response = await api.getPuzzles(huntId);
    return response;
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
  async ({ huntId, id, answer }) => {
    const response = await api.addAnswer(huntId, id, {
      answer,
    });
    return response;
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
  if (a.feeders.length == 0 && b.feeders.length > 0) {
    return -1;
  } else if (a.feeders.length > 0 && b.feeders.length == 0) {
    return 1;
  }
  // Newer puzzles before old ones
  // TODO: once creation times are added to puzzles, use those instead
  return b.id - a.id;
}

const puzzlesAdapter = createEntityAdapter();

const initialState = puzzlesAdapter.getInitialState();

export const puzzlesSlice = createSlice({
  name: "puzzles",
  initialState,
  reducers: {},
  extraReducers: {
    [addPuzzle.fulfilled]: (state, action) => {
      puzzlesAdapter.addOne(state, action.payload);
    },
    [deletePuzzle.fulfilled]: (state, action) => {
      puzzlesAdapter.removeOne(state, action.payload);
    },
    [fetchPuzzles.fulfilled]: (state, action) => {
      puzzlesAdapter.setAll(state, action.payload);
    },
    [updatePuzzle.fulfilled]: (state, action) => {
      puzzlesAdapter.updateOne(state, {
        id: action.payload.id,
        changes: { ...action.payload },
      });
    },
    [addAnswer.fulfilled]: (state, action) => {
      puzzlesAdapter.updateOne(state, {
        id: action.payload.id,
        changes: { ...action.payload },
      });
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
          row.subRows.push(rowMap[subRowId]);
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

export const { selectById: selectPuzzleById } = puzzlesSelectors;
export const { reducers } = puzzlesSlice.actions;

export default puzzlesSlice.reducer;
