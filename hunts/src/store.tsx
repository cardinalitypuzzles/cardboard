import { create } from "zustand";

import { alertSlice, AlertSlice } from "./alertSlice";
import { chatSlice, ChatSlice } from "./chatSlice";
import {
  collapsedPuzzlesSlice,
  CollapsedPuzzlesSlice,
} from "./collapsedPuzzlesSlice";
import { filterSlice, FilterSlice } from "./filterSlice";
import { huntSlice, HuntSlice } from "./huntSlice";
import { modalSlice, ModalSlice } from "./modalSlice";
import { puzzlesSlice, PuzzlesSlice } from "./puzzlesSlice";

export type RootState = AlertSlice &
  ChatSlice &
  CollapsedPuzzlesSlice &
  FilterSlice &
  HuntSlice &
  ModalSlice &
  PuzzlesSlice;

export const useStore = create<RootState>((...a) => ({
  ...alertSlice(...a),
  ...chatSlice(...a),
  ...collapsedPuzzlesSlice(...a),
  ...filterSlice(...a),
  ...huntSlice(...a),
  ...modalSlice(...a),
  ...puzzlesSlice(...a),
}));
