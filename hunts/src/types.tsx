import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import ReactTimeAgo from "react-time-ago";

import type { Row as BaseTableRow } from "react-table";

export type PuzzleId = number & { readonly __brand: unique symbol };
export type HuntId = number & { readonly __brand: unique symbol };
export type AnswerId = number & { readonly __brand: unique symbol };
export type TagId = number & { readonly __brand: unique symbol };

declare global {
  const CURRENT_HUNT_ID: HuntId;

  interface Window {
    FAVICON: string;
    LOGGED_IN_USER: string;
    APP_SHORT_TITLE: string;
  }
}

export type Hunt = {
  id: HuntId | null;
  name: string | null;
  has_drive: boolean;
  puzzle_tags: PuzzleTag[];
  create_channel_by_default: boolean;
};

export interface Puzzle {
  id: PuzzleId;
  hunt_id: HuntId;
  name: string;
  url: string;
  is_meta: boolean;
  notes: string;
  has_sheet: boolean;
  chat_room: ChatRoom | null;
  status: "SOLVING" | "SOLVED" | "PENDING" | "STUCK";
  tags: PuzzleTag[];
  guesses: PuzzleGuess[];
  metas: PuzzleId[];
  feeders: PuzzleId[];

  created_on: string;
  recent_editors: any[];
  top_editors: any[];
  last_edited_on: string | null;
}

// All the answers that are currently assigned to a given puzzle.
// If an answer is deleted, it won't be in this list.
// Should maybe be called 'answers' instead of 'guesses'?
export interface PuzzleGuess {
  id: AnswerId;
  puzzle_id: PuzzleId;
  text: string;
}

export interface PuzzleTag {
  id: TagId;
  name: string;
  color: string;
  is_meta: boolean;
  is_high_pri?: boolean;
  is_low_pri?: boolean;
  is_location?: boolean;
}

export interface ChatRoom {
  service: string;
  name: string;

  text_channel_id?: string;
  text_channel_url?: string;
  audio_channel_id?: string;
  audio_channel_url?: string;
}

export interface Row<D extends object = {}> extends BaseTableRow<D> {
  canExpand: boolean;
  isExpanded: boolean;
  depth: number;

  getToggleRowExpandedProps: any;
}

// FontAwesome typing requires the 'icon' field to be one from an
// enumeration of predefined possible strings, which can create incompatibilities
// between different versions -- in other words, if the `fa-solid` set of
// icons exposes a string that a FontAwesome component doesn't know about, it'll
// complain because the type can't be cast, even if you never use the icon.
// Typing over a set of thousands of icons is ridiculous
// so we just ignore it for this component.
// TODO: re-enable typing for FontAwesomeIcon
export const TypeIgnoredFontAwesomeIcon = FontAwesomeIcon as any;
