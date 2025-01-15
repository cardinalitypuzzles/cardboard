import React from "react";
import { DarkModeToggle } from "./DarkModeToggle";
import Drawer from "react-modern-drawer";
import { ChatVersionSelector } from "./chatSelector";
import { useSelector } from "react-redux";
import { IconMenu2 } from "@tabler/icons";
import "react-modern-drawer/dist/index.css";
import { RootState } from "./store";

import type { Hunt } from "./types";

export const SiteHeader = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const hunt = useSelector<RootState, Hunt>((state) => state.hunt);
  const toggleDrawer = () => {
    setIsOpen((prevState) => !prevState);
  };
  return (
    <>
      <nav
        className="navbar navbar-expand-lg navbar-themed"
        style={{ marginBottom: "5px" }}
      >
        <a className="navbar-brand" href="/">
          <img width="48" src={`/static/${window.FAVICON}`} alt="" />{" "}
          {window.APP_SHORT_TITLE}
        </a>
        {hunt.name}
        <button type="button" className="btn ms-auto" onClick={toggleDrawer}>
          <IconMenu2 aria-label="expand menu" />
        </button>
      </nav>
      <Drawer
        open={isOpen}
        onClose={toggleDrawer}
        direction="right"
        className="navbar-themed"
        style={{
          display: "flex",
          flexDirection: "column",
        }}
      >
        <a className="nav-link" href="/hunts">
          Back to Hunt Index
        </a>
        <a className="nav-link" href="/tools">
          Tools and References
        </a>
        <a className="nav-link" href="/accounts/logout/">
          Logout
        </a>
        <div style={{ padding: ".5rem 1rem" }}>Logged in as {window.LOGGED_IN_USER}</div>

        <div className="mt-auto" style={{ padding: ".5rem 1rem", marginBottom: "36px" }}>
          <span
            style={{
              borderTop: "1px solid black",
              width: "100%",
              display: "inline-block",
              fontWeight: "bold",
            }}
          >
            Chat Settings
          </span>
          <div style={{ padding: ".5rem 1rem" }}>
            <ChatVersionSelector />
          </div>
          <span
            style={{
              borderTop: "1px solid black",
              width: "100%",
              display: "inline-block",
              fontWeight: "bold",
              padding: ".5rem 1rem",
            }}
          >
            Appearance
          </span>
          <div style={{ padding: ".5rem 1rem" }}>
            <DarkModeToggle />
          </div>
        </div>
      </Drawer>
    </>
  );
};
