import React, { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  faChevronDown,
  faChevronUp,
  faExternalLinkAlt,
} from "@fortawesome/free-solid-svg-icons";

import { PuzzleChatSidebar } from "./PuzzleChatSidebar";
import { PuzzleId, TypeIgnoredFontAwesomeIcon } from "./types";

const DEFAULT_CHAT_WIDTH = 360;
const DEFAULT_CHAT_HEIGHT = 440;
const MIN_CHAT_WIDTH = 48;
const MIN_CHAT_HEIGHT = 48;
const CHAT_WIDTH_STORAGE_KEY = "cardboard-chat-width";
const CHAT_HEIGHT_STORAGE_KEY = "cardboard-chat-height";

type ResizeAxis = "x" | "y" | "both";

function clampChatWidth(width: number): number {
  const maxWidth = Math.max(MIN_CHAT_WIDTH, window.innerWidth);
  return Math.min(Math.max(width, MIN_CHAT_WIDTH), maxWidth);
}

function clampChatHeight(height: number): number {
  const maxHeight = Math.max(MIN_CHAT_HEIGHT, window.innerHeight);
  return Math.min(Math.max(height, MIN_CHAT_HEIGHT), maxHeight);
}

function getInitialDimension(
  storageKey: string,
  fallback: number,
  clamp: (val: number) => number
): number {
  try {
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      const parsed = parseInt(stored, 10);
      if (!Number.isNaN(parsed)) {
        return clamp(parsed);
      }
    }
  } catch {
    // Ignore localStorage access errors.
  }
  return clamp(fallback);
}

export function SheetChatApp() {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState(true);
  const [hasUnread, setHasUnread] = useState(false);
  const [chatWidth, setChatWidth] = useState<number>(() =>
    getInitialDimension(
      CHAT_WIDTH_STORAGE_KEY,
      DEFAULT_CHAT_WIDTH,
      clampChatWidth
    )
  );
  const [chatHeight, setChatHeight] = useState<number>(() =>
    getInitialDimension(
      CHAT_HEIGHT_STORAGE_KEY,
      DEFAULT_CHAT_HEIGHT,
      clampChatHeight
    )
  );
  const [isDragging, setIsDragging] = useState(false);

  const dragStartRef = useRef<{
    x: number;
    y: number;
    width: number;
    height: number;
    axis: ResizeAxis;
  } | null>(null);
  const latestSizeRef = useRef<{ width: number; height: number }>({
    width: chatWidth,
    height: chatHeight,
  });
  latestSizeRef.current = { width: chatWidth, height: chatHeight };

  const puzzleId = window.CURRENT_PUZZLE_ID as PuzzleId;
  const puzzleName = window.CURRENT_PUZZLE_NAME || "";
  const sheetUrl = window.CURRENT_SHEET_URL || "";

  useEffect(() => {
    if (!isDragging) {
      return;
    }

    const onMouseMove = (e: MouseEvent) => {
      const start = dragStartRef.current;
      if (!start) {
        return;
      }
      if (start.axis === "x" || start.axis === "both") {
        const deltaX = start.x - e.clientX;
        setChatWidth(clampChatWidth(start.width + deltaX));
      }
      if (start.axis === "y" || start.axis === "both") {
        const deltaY = start.y - e.clientY;
        setChatHeight(clampChatHeight(start.height + deltaY));
      }
    };

    const onMouseUp = () => {
      setIsDragging(false);
      dragStartRef.current = null;
      try {
        localStorage.setItem(
          CHAT_WIDTH_STORAGE_KEY,
          String(latestSizeRef.current.width)
        );
        localStorage.setItem(
          CHAT_HEIGHT_STORAGE_KEY,
          String(latestSizeRef.current.height)
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

  const handleDragStart =
    (axis: ResizeAxis) => (e: React.MouseEvent<HTMLDivElement>) => {
      e.preventDefault();
      dragStartRef.current = {
        x: e.clientX,
        y: e.clientY,
        width: chatWidth,
        height: chatHeight,
        axis,
      };
      setIsDragging(true);
    };

  const handleUnreadMessage = useCallback(() => {
    setHasUnread(true);
  }, []);

  const handleExpand = () => {
    setCollapsed(false);
    setHasUnread(false);
  };

  return (
    <div className="position-relative puzzle-chat-frame">
      <div className={`puzzle-chat-sheet${isDragging ? " is-dragging" : ""}`}>
        <iframe
          src={sheetUrl}
          title={puzzleName}
          allow="clipboard-read; clipboard-write"
          className="puzzle-chat-iframe"
        />
      </div>

      {collapsed && (
        <button
          type="button"
          className="btn puzzle-chat-toggle"
          onClick={handleExpand}
          title={t("chat-expand")}
          aria-label={t("chat-expand")}
        >
          <TypeIgnoredFontAwesomeIcon icon={faChevronUp} />
          <span>{t("chat-header")}</span>
          {hasUnread && (
            <span className="puzzle-chat-unread-dot" aria-hidden="true" />
          )}
        </button>
      )}

      <aside
        className={`puzzle-chat-sidebar${collapsed ? " d-none" : ""}`}
        style={{ width: `${chatWidth}px`, height: `${chatHeight}px` }}
      >
        <div
          aria-hidden="true"
          onMouseDown={handleDragStart("both")}
          title={t("chat-resize")}
          className="puzzle-chat-resize-corner"
        />

        <div
          role="separator"
          aria-orientation="horizontal"
          aria-label={t("chat-resize")}
          title={t("chat-resize")}
          onMouseDown={handleDragStart("y")}
          className="puzzle-chat-resize-top"
        />

        <div
          role="separator"
          aria-orientation="vertical"
          aria-label={t("chat-resize")}
          title={t("chat-resize")}
          onMouseDown={handleDragStart("x")}
          className="puzzle-chat-resize-left"
        />

        <div className="d-flex flex-column flex-grow-1 puzzle-chat-column">
          <div className="d-flex align-items-center justify-content-between gap-2 px-2 py-2 puzzle-chat-header">
            <span className="text-truncate">{t("chat-header")}</span>
            <div className="d-flex align-items-center gap-2 flex-shrink-0">
              {sheetUrl && (
                <a
                  href={sheetUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-reset text-decoration-none"
                  title={t("chat-open-sheet-new-window")}
                  aria-label={t("chat-open-sheet-new-window")}
                >
                  <TypeIgnoredFontAwesomeIcon icon={faExternalLinkAlt} />
                </a>
              )}
              <button
                type="button"
                className="btn btn-sm text-reset puzzle-chat-header-btn"
                onClick={() => setCollapsed(true)}
                title={t("chat-collapse")}
                aria-label={t("chat-collapse")}
              >
                <TypeIgnoredFontAwesomeIcon icon={faChevronDown} />
              </button>
            </div>
          </div>
          <div className="flex-grow-1 puzzle-chat-body">
            <PuzzleChatSidebar
              puzzleId={puzzleId}
              puzzleName={puzzleName}
              sheetUrl={sheetUrl}
              isCollapsed={collapsed}
              onUnreadMessage={handleUnreadMessage}
            />
          </div>
        </div>
      </aside>
    </div>
  );
}
