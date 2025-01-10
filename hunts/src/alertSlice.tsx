import { createSlice } from "@reduxjs/toolkit";
import { isRejectedAction } from "./utils";

let nextId = 1;

interface AlertState {
  show: boolean;
  variant: string;
  text: string;
  id: number;
}

export const alertSlice = createSlice({
  name: "alert",
  initialState: {
    show: false,
    variant: "",
    text: "",
    id: 0,
  } as AlertState,
  reducers: {
    showAlert: (state, action) => {
      state.show = true;
      state.variant = action.payload.variant;
      state.text = action.payload.text;
      state.id = nextId++;
    },
    hideAlert: (state) => {
      state.show = false;
    },
  },

  extraReducers: (builder) => {
    builder.addMatcher(
      isRejectedAction,
      (state, action: { error: { message?: string } }) => {
        state.show = true;
        state.variant = "danger";
        state.text = action.error.message!;
        state.id = nextId++;
      }
    );
  },
});

export const { showAlert, hideAlert } = alertSlice.actions;

export default alertSlice.reducer;
