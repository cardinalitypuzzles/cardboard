import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { updateTextFilter, getTextFilter } from "./filterSlice";

function GlobalFilter() {
  const value = useSelector(getTextFilter);
  const dispatch = useDispatch();
  return (
    <span>
      <input
        type="search"
        value={value || ""}
        onChange={(e) => {
          dispatch(updateTextFilter(e.target.value));
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
