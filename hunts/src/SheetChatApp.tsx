import React, { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  faChevronLeft,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons";

import { PuzzleChatSidebar } from "./PuzzleChatSidebar";
import { PuzzleId, TypeIgnoredFontAwesomeIcon } from "./types";

const DEFAULT_CHAT_WIDTH = 360;
const MIN_CHAT_WIDTH = 240;
const MIN_SHEET_WIDTH = 200;
const CHAT_WIDTH_STORAGE_KEY = "cardboard-chat-width";

function clampChatWidth(width: number): number {
  const maxWidth = Math.max(
    MIN_CHAT_WIDTH,
    window.innerWidth - MIN_SHEET_WIDTH
  );
  return Math.min(Math.max(width, MIN_CHAT_WIDTH), maxWidth);
}

function getInitialChatWidth(): number {
  try {
    const stored = localStorage.getItem(CHAT_WIDTH_STORAGE_KEY);
    if (stored) {
      const parsed = parseInt(stored, 10);
      if (!Number.isNaN(parsed)) {
        return clampChatWidth(parsed);
      }
    }
  } catch {
    // Ignore localStorage access errors.
  }
  return clampChatWidth(DEFAULT_CHAT_WIDTH);
}

export function SheetChatApp() {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState(false);
  const [chatWidth, setChatWidth] = useState<number>(getInitialChatWidth);
  const [isDragging, setIsDragging] = useState(false);

  const dragStartRef = useRef<{ x: number; width: number } | null>(null);
  const latestWidthRef = useRef<number>(chatWidth);
  latestWidthRef.current = chatWidth;

  const puzzleId = window.CURRENT_PUZZLE_ID as PuzzleId;
  const puzzleName = window.CURRENT_PUZZLE_NAME || "";
  const sheetUrl = window.CURRENT_SHEET_URL || "";

  useEffect(() => {
    if (!isDragging) {
      return;
    }

    const onMouseMove = (e: MouseEvent) => {
      if (!dragStartRef.current) {
        return;
      }
      const deltaX = dragStartRef.current.x - e.clientX;
      setChatWidth(clampChatWidth(dragStartRef.current.width + deltaX));
    };

    const onMouseUp = () => {
      setIsDragging(false);
      dragStartRef.current = null;
      try {
        localStorage.setItem(
          CHAT_WIDTH_STORAGE_KEY,
          String(latestWidthRef.current)
        );
      } catch {
        // Ignore localStorage access errors.
      }
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [isDragging]);

  const handleDragStart = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault();
    dragStartRef.current = { x: e.clientX, width: chatWidth };
    setIsDragging(true);
  };

  return (
    <div className="d-flex position-relative puzzle-chat-frame">
      <div
        className={`flex-grow-1 h-100 puzzle-chat-sheet${
          isDragging ? " is-dragging" : ""
        }`}
      >
        <iframe
          src={sheetUrl}
          title={puzzleName}
          allow="clipboard-read; clipboard-write"
          className="puzzle-chat-iframe"
        />
      </div>

      {collapsed ? (
        <button
          type="button"
          className="btn text-body puzzle-chat-toggle puzzle-chat-toggle-collapsed"
          onClick={() => setCollapsed(false)}
          title={t("chat-expand")}
          aria-label={t("chat-expand")}
        >
          <TypeIgnoredFontAwesomeIcon icon={faChevronLeft} />
        </button>
      ) : (
        <aside
          className="d-flex h-100 position-relative puzzle-chat-sidebar"
          style={{ width: `${chatWidth}px` }}
        >
          <button
            type="button"
            className="btn text-body puzzle-chat-toggle puzzle-chat-toggle-expanded"
            onClick={() => setCollapsed(true)}
            title={t("chat-collapse")}
            aria-label={t("chat-collapse")}
          >
            <TypeIgnoredFontAwesomeIcon icon={faChevronRight} />
          </button>

          <div
            role="separator"
            aria-orientation="vertical"
            aria-label={t("chat-resize")}
            title={t("chat-resize")}
            onMouseDown={handleDragStart}
            className="d-flex align-items-center justify-content-center user-select-none puzzle-chat-resize-handle"
          >
            <div className="puzzle-chat-resize-grip" />
          </div>

          <div className="d-flex flex-column flex-grow-1 h-100 puzzle-chat-column">
            <div className="px-2 py-2 puzzle-chat-header">
              {t("chat-header")}
            </div>
            <div className="flex-grow-1 puzzle-chat-body">
              <PuzzleChatSidebar puzzleId={puzzleId} puzzleName={puzzleName} />
            </div>
          </div>
        </aside>
      )}
    </div>
  );
}
