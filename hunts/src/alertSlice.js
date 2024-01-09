import { createSlice } from "@reduxjs/toolkit";
import { isRejectedAction } from "./utils";

let nextId = 1;

export const alertSlice = createSlice({
  name: "alert",
  initialState: {
    show: false,
    variant: null,
    text: "",
    id: 0,
  },
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
    builder.addMatcher(isRejectedAction, (state, action) => {
      state.show = true;
      state.variant = "danger";
      state.text = action.error.message;
      state.id = nextId++;
    });
  },
});

export const { showAlert, hideAlert } = alertSlice.actions;

export default alertSlice.reducer;
