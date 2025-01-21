import { StateCreator } from "zustand";

import { RootState } from "./store";

enum AlertWindowType {
  SUCCESS = "success",
  DANGER = "danger",
  WARNING = "warning",
  INFO = "info",
}

export interface AlertSlice {
  alertSlice: {
    show: boolean;
    variant: AlertWindowType;
    text: string;
    id: number;

    showAlert: (variant: AlertWindowType, text: string) => void;
    hideAlert: () => void;
  };
}

let nextId = 1;

export const alertSlice: StateCreator<
  RootState,
  [["zustand/immer", never]],
  [],
  AlertSlice
> = (set, get) => ({
  alertSlice: {
    show: false,
    variant: AlertWindowType.INFO,
    text: "",
    id: 0,

    showAlert: (variant: AlertWindowType, text: string) => {
      set((state) => {
        state.alertSlice.show = true;
        state.alertSlice.variant = variant;
        state.alertSlice.text = text;
        state.alertSlice.id = nextId++;
      });
    },
    hideAlert: () => {
      set((state) => {
        state.alertSlice.show = false;
      });
    },
  },
});

export default alertSlice;
