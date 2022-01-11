export const DEFAULT_TAG_COLOR = "primary";
export const SELECTABLE_TAG_COLORS = [
  { color: "primary", display: "Blue" },
  { color: "light", display: "White" },
];
// TODO(#527): Store these in the backend and read them from an API call
export const DEFAULT_TAGS = [
  { name: "High priority", color: "danger" },
  { name: "Low priority", color: "warning" },
  { name: "Backsolved", color: "success" },
  { name: "Slog", color: "secondary" },

  { name: "Grid logic", color: "light" },
  { name: "Non-grid logic", color: "light" },

  { name: "Crossword", color: "primary" },
  { name: "Cryptics", color: "primary" },
  { name: "Wordplay", color: "primary" },

  { name: "Media manipulation", color: "light" },
  { name: "Programming", color: "light" },

  { name: "Art ID", color: "primary" },
  { name: "Bio", color: "primary" },
  { name: "Chem", color: "primary" },
  { name: "Foreign languages", color: "primary" },
  { name: "Geography", color: "primary" },
  { name: "Literature", color: "primary" },
  { name: "Math", color: "primary" },
  { name: "Physics", color: "primary" },

  { name: "Anime", color: "light" },
  { name: "Board games", color: "light" },
  // older pop culture
  { name: "Boomer", color: "light" },
  { name: "Knitting", color: "light" },
  { name: "Movies", color: "light" },
  { name: "Music ID", color: "light" },
  { name: "Sports", color: "light" },
  { name: "TV", color: "light" },
  { name: "Video games", color: "light" },
  // newer pop culture
  { name: "Zoomer", color: "light" },

  { name: "MIT", color: "primary" },
  { name: "Printing", color: "primary" },
  { name: "Teamwork", color: "primary" },
];

export const SHEET_REDIRECT_BASE = "/puzzles/s";
export const CHAT_PLATFORM = "discord";
