import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

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
});

export const { showModal, hideModal } = modalSlice.actions;

export default modalSlice.reducer;
