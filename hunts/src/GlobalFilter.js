import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { updateTextFilter, getTextFilter } from "./filterSlice";

function GlobalFilter() {
  const value = useSelector(getTextFilter);
  const dispatch = useDispatch();
  return (
    <span>
      <input
        value={value || ""}
        onChange={(e) => {
          dispatch(updateTextFilter(e.target.value));
        }}
        placeholder={"Search"}
      />
    </span>
  );
}

export default GlobalFilter;
