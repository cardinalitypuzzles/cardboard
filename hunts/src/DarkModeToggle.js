import React from "react";

const isCurrentlyDark = () => {
  return localStorage.getItem("cardboard-theme") === "bootstrap-dark";
};

export const DarkModeToggle = () => {
  const [isDark, setIsDark] = React.useState(isCurrentlyDark());
  return (
    <>
      <div className="form-check">
        <input
          type="checkbox"
          id="dark-mode-checkbox"
          className="form-check-input"
          checked={isDark}
          onChange={(e) => {
            if (isDark) {
              // Light
              document.body.classList.remove("bootstrap-dark");
              document.body.classList.add("bootstrap");
              localStorage.setItem("cardboard-theme", "bootstrap");
            } else {
              // Dark
              document.body.classList.remove("bootstrap");
              document.body.classList.add("bootstrap-dark");
              localStorage.setItem("cardboard-theme", "bootstrap-dark");
            }
            setIsDark(e.target.checked);
          }}
        />
        <label className="form-check-label" htmlFor="dark-mode-checkbox">
          Dark Mode
        </label>
      </div>
    </>
  );
};
