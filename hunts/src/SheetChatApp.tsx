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

const CARDINAL_BORDER_COLOR =
  "color-mix(in srgb, #b81d38 40%, var(--bs-border-color))";
const CARDINAL_DIVIDER_INNER_BORDER =
  "color-mix(in srgb, #b81d38 18%, var(--bs-border-color))";
const CARDINAL_HANDLE_BG = "color-mix(in srgb, #b81d38 11%, var(--bs-body-bg))";
const CARDINAL_SIDEBAR_BG = "color-mix(in srgb, #b81d38 5%, var(--bs-body-bg))";
const CARDINAL_GRIP_COLOR =
  "color-mix(in srgb, #b81d38 50%, var(--bs-secondary-color))";

function clampChatWidth(width: number): number {
  const maxWidth =
    typeof window !== "undefined"
      ? Math.max(MIN_CHAT_WIDTH, window.innerWidth - MIN_SHEET_WIDTH)
      : 800;
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

const folderTabStyle: React.CSSProperties = {
  position: "absolute",
  top: "72px",
  width: "28px",
  height: "44px",
  padding: 0,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  backgroundColor: CARDINAL_HANDLE_BG,
  borderTop: `2px solid ${CARDINAL_BORDER_COLOR}`,
  borderBottom: `2px solid ${CARDINAL_BORDER_COLOR}`,
  borderLeft: `2px solid ${CARDINAL_BORDER_COLOR}`,
  borderRight: "none",
  borderTopLeftRadius: "6px",
  borderBottomLeftRadius: "6px",
  borderTopRightRadius: 0,
  borderBottomRightRadius: 0,
  zIndex: 20,
};

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
    <div
      className="d-flex position-relative"
      style={{ height: "100vh", width: "100vw" }}
    >
      <div
        className="flex-grow-1 h-100"
        style={{
          minWidth: 0,
          pointerEvents: isDragging ? "none" : "auto",
        }}
      >
        <iframe
          src={sheetUrl}
          title={puzzleName}
          allow="clipboard-read; clipboard-write"
          style={{ width: "100%", height: "100%", border: 0 }}
        />
      </div>

      {collapsed ? (
        <button
          type="button"
          className="btn text-body"
          style={{ ...folderTabStyle, right: 0 }}
          onClick={() => setCollapsed(false)}
          title={t("chat-expand")}
          aria-label={t("chat-expand")}
        >
          <TypeIgnoredFontAwesomeIcon icon={faChevronLeft} />
        </button>
      ) : (
        <aside
          className="d-flex h-100 position-relative"
          style={{
            width: `${chatWidth}px`,
            flexShrink: 0,
            backgroundColor: CARDINAL_SIDEBAR_BG,
          }}
        >
          <button
            type="button"
            className="btn text-body"
            style={{ ...folderTabStyle, right: "100%" }}
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
            className="d-flex align-items-center justify-content-center user-select-none"
            style={{
              width: "8px",
              flexShrink: 0,
              cursor: "col-resize",
              backgroundColor: CARDINAL_HANDLE_BG,
              borderLeft: `2px solid ${CARDINAL_BORDER_COLOR}`,
              borderRight: `1px solid ${CARDINAL_DIVIDER_INNER_BORDER}`,
            }}
          >
            <div
              style={{
                width: "3px",
                height: "32px",
                borderRadius: "2px",
                backgroundColor: CARDINAL_GRIP_COLOR,
              }}
            />
          </div>

          <div
            className="d-flex flex-column flex-grow-1 h-100"
            style={{ minWidth: 0, minHeight: 0 }}
          >
            <style>{`
              .puzzle-chat-header {
                color: #8b172c;
                font-size: 1.05rem;
                font-weight: 700;
                letter-spacing: -0.01em;
              }
              [data-bs-theme="dark"] .puzzle-chat-header {
                color: #ea868f;
              }
            `}</style>
            <div
              className="px-2 py-2 puzzle-chat-header"
              style={{
                backgroundColor: CARDINAL_HANDLE_BG,
                borderBottom: `1px solid ${CARDINAL_DIVIDER_INNER_BORDER}`,
              }}
            >
              {t("chat-header")}
            </div>
            <div className="flex-grow-1" style={{ minHeight: 0 }}>
              <PuzzleChatSidebar puzzleId={puzzleId} puzzleName={puzzleName} />
            </div>
          </div>
        </aside>
      )}
    </div>
  );
}
