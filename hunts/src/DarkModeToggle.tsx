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
            let newTheme = isDark ? 'light' : 'dark';
            document.body.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('cardboard-theme', newTheme);
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
