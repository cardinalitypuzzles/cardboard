import { configureStore } from "@reduxjs/toolkit";
import puzzlesReducer from "./puzzlesSlice";
import huntReducer from "./huntSlice";
import modalReducer from "./modalSlice";
import alertReducer from "./alertSlice";
import filterReducer from "./filterSlice";
import { save, load } from "redux-localstorage-simple";

const preloadedState = load({
  states: ["filter.solveStateFilter", "filter.tags"],
});

export default configureStore({
  reducer: {
    modal: modalReducer,
    alert: alertReducer,
    puzzles: puzzlesReducer,
    hunt: huntReducer,
    filter: filterReducer,
  },
  middleware: (getDefaultMiddlewares) => [
    ...getDefaultMiddlewares(),
    save({
      states: ["filter.solveStateFilter", "filter.tags"],
    }),
  ],
  preloadedState,
});
