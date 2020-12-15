import React from "react";

function GlobalFilter({ globalFilter, setGlobalFilter }) {
  const [value, setValue] = React.useState(globalFilter);

  return (
    <span>
      <input
        value={value || ""}
        onChange={(e) => {
          setValue(e.target.value);
          setGlobalFilter(e.target.value);
        }}
        placeholder={"Search"}
      />
    </span>
  );
}

export default GlobalFilter;
