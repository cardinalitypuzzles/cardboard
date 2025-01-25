import React from "react";
import { useStore } from "./store";

function GlobalFilter() {
  const { filterValue, setFilterValue } = useStore(
    (state) => state.filterSlice
  );
  return (
    <span>
      <input
        type="search"
        value={filterValue || ""}
        onChange={(e) => {
          setFilterValue(e.target.value);
        }}
        placeholder="Search by name, answer, tag, etc."
        style={{
          width: "260",
          marginRight: "8",
        }}
      />
    </span>
  );
}

export default GlobalFilter;
