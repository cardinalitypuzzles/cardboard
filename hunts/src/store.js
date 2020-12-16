import { configureStore } from "@reduxjs/toolkit";
import puzzlesReducer from "./puzzlesSlice";
import huntReducer from "./huntSlice";
import modalReducer from "./modalSlice";
import alertReducer from "./alertSlice";

export default configureStore({
  reducer: {
    modal: modalReducer,
    alert: alertReducer,
    puzzles: puzzlesReducer,
    hunt: huntReducer,
  },
});
