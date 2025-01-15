import React from "react";

const isCurrentlyDark = () => {
  return localStorage.getItem("cardboard-theme") === "dark";
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
              localStorage.setItem("cardboard-theme", "light");
              document.body.setAttribute('data-bs-theme', 'light');
            } else {
              localStorage.setItem("cardboard-theme", "dark");
              document.body.setAttribute('data-bs-theme', 'dark');
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
