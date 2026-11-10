import React from "react";
import { useTranslation } from "react-i18next";
import { useStore } from "./store";

function GlobalFilter() {
  const { filterValue, setFilterValue } = useStore(
    (state) => state.filterSlice
  );
  const { t } = useTranslation();

  return (
    <span>
      <input
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
