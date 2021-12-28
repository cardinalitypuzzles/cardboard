import { configureStore } from "@reduxjs/toolkit";
import puzzlesReducer from "./puzzlesSlice";
import huntReducer from "./huntSlice";
import modalReducer from "./modalSlice";
import alertReducer from "./alertSlice";
import tagFilterReducer from "./tagFilterSlice";
import filterReducer from './filterSlice';
import { save, load } from 'redux-localstorage-simple';

const preloadedState = load({
  states: ["filter.solveStateFilter"],
});

export default configureStore({
  reducer: {
    modal: modalReducer,
    alert: alertReducer,
    puzzles: puzzlesReducer,
    hunt: huntReducer,
    tagFilter: tagFilterReducer,
    filter: filterReducer,
  },
  middleware: (getDefaultMiddlewares) => [
    ...getDefaultMiddlewares(),
    save({
      states: ["filter.solveStateFilter"],
    })
  ],
  preloadedState,
});
