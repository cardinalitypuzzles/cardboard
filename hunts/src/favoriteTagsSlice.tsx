import { StateCreator } from "zustand";

import type { RootState } from "./store";

const STORAGE_KEY = "cardboard-favorite-tags";

const loadFavorites = (): string[] => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed
        .filter((x): x is string => typeof x === "string")
        .map((x) => x.toLowerCase());
    }
  } catch {
    // Ignore storage read/parse errors
  }
  return [];
};

const saveFavorites = (favorites: string[]) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites));
  } catch {
    // Ignore storage write errors
  }
};

export interface FavoriteTagsSlice {
  favoriteTagsSlice: {
    favoriteTagNames: string[];
    isFavoriteTag: (name: string) => boolean;
    toggleFavoriteTag: (name: string) => void;
    removeFavoriteTag: (name: string) => void;
  };
}

export const favoriteTagsSlice: StateCreator<
  RootState,
  [["zustand/devtools", never], ["zustand/immer", never]],
  [],
  FavoriteTagsSlice
> = (set, get) => ({
  favoriteTagsSlice: {
    favoriteTagNames: loadFavorites(),

    isFavoriteTag: (name: string) => {
      const normalized = name.trim().toLowerCase();
      if (!normalized) {
        return false;
      }
      return get().favoriteTagsSlice.favoriteTagNames.includes(normalized);
    },

    toggleFavoriteTag: (name: string) => {
      const normalized = name.trim().toLowerCase();
      if (!normalized) {
        return;
      }
      set((state) => {
        const current = state.favoriteTagsSlice.favoriteTagNames;
        const next = current.includes(normalized)
          ? current.filter((n) => n !== normalized)
          : [...current, normalized];
        state.favoriteTagsSlice.favoriteTagNames = next;
        saveFavorites(next);
      });
    },

    removeFavoriteTag: (name: string) => {
      const normalized = name.trim().toLowerCase();
      if (!normalized) {
        return;
      }
      set((state) => {
        const current = state.favoriteTagsSlice.favoriteTagNames;
        if (!current.includes(normalized)) {
          return;
        }
        const next = current.filter((n) => n !== normalized);
        state.favoriteTagsSlice.favoriteTagNames = next;
        saveFavorites(next);
      });
    },
  },
});

export default favoriteTagsSlice;
