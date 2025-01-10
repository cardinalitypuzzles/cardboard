import { configureStore } from "@reduxjs/toolkit";
import puzzlesReducer from "./puzzlesSlice";
import huntReducer from "./huntSlice";
import modalReducer from "./modalSlice";
import alertReducer from "./alertSlice";
import filterReducer from "./filterSlice";
import chatReducer from "./chatSlice";
import collapsedPuzzleReducer from "./collapsedPuzzlesSlice";
import { save, load } from "redux-localstorage-simple";

const preloadedState = load({
  states: [
    "filter.solveStateFilter",
    "filter.tags",
    "chat.version",
    "collapsedPuzzles",
  ],
});

const store = configureStore({
  reducer: {
    modal: modalReducer,
    alert: alertReducer,
    collapsedPuzzles: collapsedPuzzleReducer,
    puzzles: puzzlesReducer,
    hunt: huntReducer,
    filter: filterReducer,
    chat: chatReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      save({
        states: [
          "filter.solveStateFilter",
          "filter.tags",
          "chat.version",
          "collapsedPuzzles",
        ],
      })
    ),
  preloadedState,
});

export type RootState = ReturnType<typeof store.getState>;
export type Dispatch = typeof store.dispatch;

export default store;
