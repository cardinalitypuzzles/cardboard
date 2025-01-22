import { StateCreator } from "zustand";

import { RootState } from "./store";

export interface ModalSlice {
  modalSlice: {
    show: boolean;
    type: string;
    props: Record<string, any>;

    showModal: (payload: { type: string; props: any }) => void;
    hideModal: () => void;
  };
}

export const modalSlice: StateCreator<
  RootState,
  [["zustand/devtools", never], ["zustand/immer", never]],
  [],
  ModalSlice
> = (set, get) => ({
  modalSlice: {
    show: false,
    type: "",
    props: {},

    showModal: (payload: { type: string; props: any }) => {
      set((state) => {
        state.modalSlice.show = true;
        state.modalSlice.type = payload.type;
        state.modalSlice.props = payload.props;
      });
    },
    hideModal: () => {
      set((state) => {
        state.modalSlice.show = false;
      });
    },
  },
});
