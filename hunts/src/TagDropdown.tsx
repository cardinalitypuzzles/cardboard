import React from "react";
import { createPortal } from "react-dom";
import TagPill from "./TagPill";
import type { PuzzleTag } from "./types";

function TagDropdown({
  tags,
  selectedTag,
  onSelect,
}: {
  tags: PuzzleTag[];
  selectedTag: PuzzleTag;
  onSelect: (tag: PuzzleTag) => void;
}) {
  const [open, setOpen] = React.useState(false);
  const [anchorRect, setAnchorRect] = React.useState<DOMRect | null>(null);
  const triggerRef = React.useRef<HTMLButtonElement | null>(null);
  const menuRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!open) {
      return;
    }
    const handleMouseDown = (e: MouseEvent) => {
      const target = e.target as Node | null;
      if (
        target &&
        !triggerRef.current?.contains(target) &&
        !menuRef.current?.contains(target)
      ) {
        setOpen(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        setOpen(false);
      }
    };
    const handleScrollOrResize = (e: Event) => {
      if (e.target instanceof Node && menuRef.current?.contains(e.target)) {
        return;
      }
      if (triggerRef.current) {
        setAnchorRect(triggerRef.current.getBoundingClientRect());
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
  }, [open]);

  const menuStyle = React.useMemo((): React.CSSProperties | null => {
    if (!open || !anchorRect) {
      return null;
    }
    const spaceBelow = window.innerHeight - anchorRect.bottom;
    const placeBelow = spaceBelow >= 230 || spaceBelow >= anchorRect.top;
    const centerX = anchorRect.left + anchorRect.width / 2;

    return {
      left: `${centerX}px`,
      transform: "translateX(-50%)",
      ...(placeBelow
        ? { top: `${anchorRect.bottom + 4}px` }
        : { bottom: `${window.innerHeight - anchorRect.top + 4}px` }),
      zIndex: 1080,
      maxHeight: "220px",
      width: "max-content",
      minWidth: "120px",
      maxWidth: "280px",
    };
  }, [open, anchorRect]);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        className="border-0 bg-transparent px-0 d-inline-flex align-items-center gap-1 text-body flex-shrink-0"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => {
          if (open) {
            setOpen(false);
          } else if (triggerRef.current) {
            setAnchorRect(triggerRef.current.getBoundingClientRect());
            setOpen(true);
          }
        }}
        style={{
          paddingTop: "2px",
          paddingBottom: "2px",
          cursor: "pointer",
        }}
      >
        <TagPill
          name={selectedTag.name}
          color={selectedTag.color}
          isMeta={selectedTag.is_meta}
        />
        <span className="small opacity-75">▾</span>
      </button>
      {menuStyle &&
        createPortal(
          <div
            ref={menuRef}
            role="listbox"
            className="position-fixed overflow-y-auto bg-body border rounded shadow p-1"
            style={menuStyle}
          >
            {tags.map((tag) => {
              const isSelected = tag.id === selectedTag.id;
              return (
                <button
                  key={tag.id}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  className={`d-block w-100 text-start border-0 rounded-1 lh-1 ${
                    isSelected ? "bg-body-tertiary" : "bg-transparent"
                  }`}
                  onClick={() => {
                    onSelect(tag);
                    setOpen(false);
                  }}
                  style={{
                    padding: "2px 4px",
                    cursor: "pointer",
                  }}
                >
                  <TagPill
                    name={tag.name}
                    color={tag.color}
                    isMeta={tag.is_meta}
                    noMargin={true}
                  />
                </button>
              );
            })}
          </div>,
          document.body
        )}
    </>
  );
}

export default TagDropdown;
