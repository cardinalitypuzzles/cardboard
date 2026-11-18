import React from "react";
import { useTranslation } from "react-i18next";
import { useStore } from "./store";

function GlobalFilter() {
  const { filterValue, setFilterValue } = useStore(
    (state) => state.filterSlice
  );
  const modalShow = useStore((state) => state.modalSlice.show);
  const { t } = useTranslation();
  const inputRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) {
        return;
      }
      if (modalShow || document.activeElement === inputRef.current) {
        return;
      }
      const target = e.target as HTMLElement | null;
      if (target) {
        const tagName = target.tagName;
        if (
          tagName === "TEXTAREA" ||
          tagName === "SELECT" ||
          target.isContentEditable
        ) {
          return;
        }
        if (tagName === "INPUT") {
          const inputType = (target as HTMLInputElement).type;
          if (
            inputType !== "checkbox" &&
            inputType !== "radio" &&
            inputType !== "button" &&
            inputType !== "submit" &&
            inputType !== "reset"
          ) {
            return;
          }
        }
      }
      e.preventDefault();
      inputRef.current?.focus();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [modalShow]);

  return (
    <span>
      <input
        ref={inputRef}
        type="search"
        value={filterValue || ""}
        onChange={(e) => {
          setFilterValue(e.target.value);
        }}
        placeholder={t("filter-placeholder")}
        style={{
          width: "260",
          marginRight: "8",
        }}
      />
    </span>
  );
}

export default GlobalFilter;
