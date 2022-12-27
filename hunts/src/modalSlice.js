import { createSlice } from "@reduxjs/toolkit";
import { isRejectedAction } from "./utils";

export const modalSlice = createSlice({
  name: "modal",
  initialState: {
    show: false,
    type: null,
    props: {},
  },
  reducers: {
    showModal: (state, action) => {
      state.show = true;
      state.type = action.payload.type;
      state.props = action.payload.props;
    },
    hideModal: (state) => {
      state.show = false;
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(isRejectedAction, (state) => {
      // On any error, the modal should close, so that the alert is visible.
      // Might need something more precise later but this is good enough for now.
      state.show = false;
    });
  },
});

export const { showModal, hideModal } = modalSlice.actions;

export default modalSlice.reducer;
