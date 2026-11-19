import React from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import { SELECTABLE_TAG_COLORS } from "./constants";
import { isLightColor } from "./utils";

// A simple 3x4 color palette selector
function ColorPicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (color: string) => void;
}) {
  const { t } = useTranslation();
  const [show, setShow] = React.useState(false);
  const [anchorRect, setAnchorRect] = React.useState<DOMRect | null>(null);
  const targetRef = React.useRef<HTMLButtonElement | null>(null);
  const popoverRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!show) {
      return;
    }
    const handleMouseDown = (e: MouseEvent) => {
      const target = e.target as Node | null;
      if (
        target &&
        !targetRef.current?.contains(target) &&
        !popoverRef.current?.contains(target)
      ) {
        setShow(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        setShow(false);
      }
    };
    const handleScrollOrResize = () => {
      if (targetRef.current) {
        setAnchorRect(targetRef.current.getBoundingClientRect());
      }
    };

    document.addEventListener("mousedown", handleMouseDown);
    document.addEventListener("keydown", handleKeyDown, true);
    window.addEventListener("scroll", handleScrollOrResize, true);
    window.addEventListener("resize", handleScrollOrResize);
    return () => {
      document.removeEventListener("mousedown", handleMouseDown);
      document.removeEventListener("keydown", handleKeyDown, true);
      window.removeEventListener("scroll", handleScrollOrResize, true);
      window.removeEventListener("resize", handleScrollOrResize);
    };
  }, [show]);

  const currentEntry = Object.entries(SELECTABLE_TAG_COLORS).find(
    ([, [, color]]) => color === value
  );
  const currentLabel = currentEntry ? t(currentEntry[0]) : value;

  const popoverStyle = React.useMemo((): React.CSSProperties | null => {
    if (!show || !anchorRect) {
      return null;
    }
    const POPOVER_WIDTH = 154;
    const POPOVER_HEIGHT = 118;
    const GAP = 6;
    const MARGIN = 8;
    const spaceBelow = window.innerHeight - anchorRect.bottom - GAP;
    const placeAbove =
      spaceBelow < POPOVER_HEIGHT + MARGIN &&
      anchorRect.top > POPOVER_HEIGHT + GAP + MARGIN;
    const top = placeAbove
      ? anchorRect.top - POPOVER_HEIGHT - GAP
      : anchorRect.bottom + GAP;
    const left = Math.max(
      MARGIN,
      Math.min(anchorRect.left, window.innerWidth - POPOVER_WIDTH - MARGIN)
    );
    return {
      left: `${Math.round(left)}px`,
      top: `${Math.round(top)}px`,
      width: `${POPOVER_WIDTH}px`,
      height: `${POPOVER_HEIGHT}px`,
      zIndex: 1080,
    };
  }, [show, anchorRect]);

  return (
    <>
      <button
        ref={targetRef}
        type="button"
        className="btn border bg-body d-inline-flex align-items-center gap-1 px-2 flex-shrink-0"
        title={currentLabel}
        aria-label={currentLabel}
        aria-expanded={show}
        onClick={() => {
          if (show) {
            setShow(false);
          } else if (targetRef.current) {
            setAnchorRect(targetRef.current.getBoundingClientRect());
            setShow(true);
          }
        }}
        style={{ cursor: "pointer" }}
      >
        <span
          className="rounded-circle border d-inline-block"
          style={{
            backgroundColor: value,
            width: "24px",
            height: "24px",
          }}
        />
        <span className="small opacity-75">▾</span>
      </button>
      {popoverStyle &&
        createPortal(
          <div
            ref={popoverRef}
            className="position-fixed bg-body border rounded shadow p-2"
            style={popoverStyle}
          >
            <div
              className="d-grid gap-2"
              style={{
                gridTemplateColumns: "repeat(4, 28px)",
              }}
            >
              {Object.entries(SELECTABLE_TAG_COLORS).map(([key, [, color]]) => {
                const isSelected = value === color;
                const useDarkText = isLightColor(color);
                return (
                  <button
                    key={color}
                    type="button"
                    className={`rounded-circle p-0 d-flex align-items-center justify-content-center lh-1 ${
                      isSelected ? "" : "border"
                    }`}
                    title={t(key)}
                    aria-label={t(key)}
                    aria-pressed={isSelected}
                    onClick={() => {
                      onChange(color);
                      setShow(false);
                    }}
                    style={{
                      backgroundColor: color,
                      color: useDarkText ? "#000000" : "#ffffff",
                      width: "28px",
                      height: "28px",
                      fontSize: "0.8rem",
                      cursor: "pointer",
                      ...(isSelected
                        ? {
                            border: "2px solid #5BC0DE",
                            boxShadow: "0 0 2px #5BC0DE",
                          }
                        : {}),
                    }}
                  >
                    {isSelected ? "✓" : ""}
                  </button>
                );
              })}
            </div>
          </div>,
          document.body
        )}
    </>
  );
}

export default ColorPicker;
