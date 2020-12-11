import { configureStore } from "@reduxjs/toolkit";
import puzzlesReducer from "./puzzlesSlice";
import huntReducer from "./huntSlice";
import modalReducer from "./modalSlice";

export default configureStore({
  reducer: {
    modal: modalReducer,
    puzzles: puzzlesReducer,
    hunt: huntReducer,
  },
});
