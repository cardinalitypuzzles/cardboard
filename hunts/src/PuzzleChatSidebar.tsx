import React, { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import ReactTimeAgo from "react-time-ago";
import { faImage, faTimes } from "@fortawesome/free-solid-svg-icons";

import api from "./api";
import { resizeImageFile } from "./imageUtils";
import {
  PuzzleChatMessage,
  PuzzleId,
  TypeIgnoredFontAwesomeIcon,
} from "./types";

const POLL_INTERVAL_MS = 2500;
const MAX_IMAGE_DIMENSION = 1000;
const URL_REGEX = /(https?:\/\/[^\s]+)/g;
const CARDINAL_DIVIDER_COLOR =
  "color-mix(in srgb, #b81d38 22%, var(--bs-border-color))";

function renderMessageText(text: string) {
  const parts = text.split(URL_REGEX);
  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return (
        <a
          key={index}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          style={{ wordBreak: "break-all" }}
        >
          {part}
        </a>
      );
    }
    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
}

interface PuzzleChatSidebarProps {
  puzzleId: PuzzleId;
  puzzleName: string;
}

export function PuzzleChatSidebar({
  puzzleId,
  puzzleName,
}: PuzzleChatSidebarProps) {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<PuzzleChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("");
  const [pendingImage, setPendingImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lastMessageIdRef = useRef<number | undefined>(undefined);
  const listRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const shouldScrollRef = useRef(true);

  const appendMessages = useCallback((incoming: PuzzleChatMessage[]) => {
    if (incoming.length === 0) {
      return;
    }
    const listEl = listRef.current;
    if (listEl) {
      const distanceFromBottom =
        listEl.scrollHeight - listEl.scrollTop - listEl.clientHeight;
      shouldScrollRef.current = distanceFromBottom < 60;
    }
    setMessages((prev) => {
      const existingIds = new Set(prev.map((m) => m.id));
      const merged = [...prev];
      for (const msg of incoming) {
        if (!existingIds.has(msg.id)) {
          merged.push(msg);
          existingIds.add(msg.id);
        }
      }
      if (merged.length > 0) {
        lastMessageIdRef.current = merged[merged.length - 1].id;
      }
      return merged;
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setMessages([]);
    lastMessageIdRef.current = undefined;
    shouldScrollRef.current = true;

    api
      .getPuzzleChatMessages(puzzleId)
      .then((initialMessages) => {
        if (cancelled) {
          return;
        }
        setMessages(initialMessages);
        if (initialMessages.length > 0) {
          lastMessageIdRef.current =
            initialMessages[initialMessages.length - 1].id;
        }
        setError(null);
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [puzzleId]);

  useEffect(() => {
    let cancelled = false;
    const poll = () => {
      if (document.visibilityState === "hidden") {
        return;
      }
      api
        .getPuzzleChatMessages(puzzleId, lastMessageIdRef.current)
        .then((newer) => {
          if (!cancelled) {
            appendMessages(newer);
          }
        })
        .catch(() => {
          // Ignore transient polling failures; next tick will retry.
        });
    };

    const intervalId = window.setInterval(poll, POLL_INTERVAL_MS);
    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        poll();
      }
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [puzzleId, appendMessages]);

  useEffect(() => {
    if (shouldScrollRef.current && listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
      shouldScrollRef.current = false;
    }
  }, [messages, loading]);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) {
      return;
    }
    el.style.height = "auto";
    el.style.height = `${Math.max(32, Math.min(el.scrollHeight, 100))}px`;
  }, [text]);

  const attachImage = async (file: File) => {
    setError(null);
    try {
      const resized = await resizeImageFile(file, MAX_IMAGE_DIMENSION);
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      setPendingImage(resized);
      setPreviewUrl(URL.createObjectURL(resized));
      textareaRef.current?.focus();
    } catch {
      setError(t("chat-error-unsupported-image"));
    }
  };

  const clearPendingImage = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPendingImage(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const items = e.clipboardData?.items;
    if (!items) {
      return;
    }
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.startsWith("image/")) {
        const file = item.getAsFile();
        if (file) {
          e.preventDefault();
          void attachImage(file);
          return;
        }
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      void attachImage(file);
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    const trimmed = text.trim();
    if ((!trimmed && !pendingImage) || sending) {
      return;
    }
    setSending(true);
    setError(null);
    try {
      const created = await api.sendPuzzleChatMessage(
        puzzleId,
        trimmed,
        pendingImage
      );
      shouldScrollRef.current = true;
      appendMessages([created]);
      setText("");
      clearPendingImage();
    } catch (err: any) {
      setError(err?.message || "Failed to send message");
    } finally {
      setSending(false);
      requestAnimationFrame(() => {
        textareaRef.current?.focus();
      });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="d-flex flex-column h-100 text-body">
      <style>{".puzzle-chat-input::placeholder { opacity: 0.45; }"}</style>
      <div
        ref={listRef}
        className="flex-grow-1 overflow-auto p-2"
        aria-label={puzzleName}
      >
        {loading ? (
          <div className="text-muted small p-2">{t("chat-loading")}</div>
        ) : messages.length === 0 ? (
          <div className="text-muted small p-2" style={{ opacity: 0.55 }}>
            {t("chat-empty")}
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className="mb-2 pb-2"
              style={{ borderBottom: `1px solid ${CARDINAL_DIVIDER_COLOR}` }}
            >
              <div className="d-flex justify-content-between align-items-baseline gap-2">
                <strong className="small text-truncate">{msg.user_name}</strong>
                <span className="text-muted" style={{ fontSize: "0.75rem" }}>
                  <ReactTimeAgo date={new Date(msg.created_on)} />
                </span>
              </div>
              {msg.text && (
                <div
                  className="small mt-1"
                  style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}
                >
                  {renderMessageText(msg.text)}
                </div>
              )}
              {msg.image_url && (
                <div className="mt-1">
                  <a
                    href={msg.image_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <img
                      src={msg.image_url}
                      alt={t("chat-image-alt")}
                      className="img-fluid rounded border"
                      style={{ maxHeight: "300px", objectFit: "contain" }}
                    />
                  </a>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <form
        onSubmit={handleSend}
        className="p-2"
        style={{ borderTop: `1px solid ${CARDINAL_DIVIDER_COLOR}` }}
      >
        {error && (
          <div className="alert alert-danger py-1 px-2 small mb-2" role="alert">
            {error}
          </div>
        )}
        {previewUrl && (
          <div className="mb-2 d-flex align-items-start gap-2">
            <img
              src={previewUrl}
              alt={t("chat-image-alt")}
              className="rounded border"
              style={{
                maxHeight: "120px",
                maxWidth: "220px",
                objectFit: "contain",
              }}
            />
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              onClick={clearPendingImage}
              title={t("chat-remove-image")}
              aria-label={t("chat-remove-image")}
            >
              <TypeIgnoredFontAwesomeIcon icon={faTimes} />
            </button>
          </div>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/gif,image/webp"
          className="d-none"
          onChange={handleFileChange}
        />
        <div className="d-flex align-items-end gap-2">
          <textarea
            ref={textareaRef}
            className="form-control form-control-sm puzzle-chat-input flex-grow-1"
            rows={1}
            placeholder={t("chat-placeholder")}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onPaste={handlePaste}
            onKeyDown={handleKeyDown}
            readOnly={sending}
            style={{
              resize: "none",
              minHeight: "32px",
              maxHeight: "100px",
              overflowY: "auto",
            }}
          />
          <button
            type="button"
            className="btn btn-sm btn-outline-secondary flex-shrink-0"
            style={{
              width: "32px",
              height: "32px",
              minWidth: "32px",
              minHeight: "32px",
              padding: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onClick={() => fileInputRef.current?.click()}
            title={t("chat-attach-image")}
            aria-label={t("chat-attach-image")}
            disabled={sending}
          >
            <TypeIgnoredFontAwesomeIcon icon={faImage} />
          </button>
        </div>
      </form>
    </div>
  );
}
