import React from "react";
import { DarkModeToggle } from "./DarkModeToggle";
import Drawer from "react-modern-drawer";
import { ChatVersionSelector } from "./chatSelector";
import { useSelector } from "react-redux";
import { IconMenu2 } from "@tabler/icons";
import "react-modern-drawer/dist/index.css";

export const SiteHeader = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const hunt = useSelector((state) => state.hunt);
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
          <img height="40" src="/static/favicon.ico" alt="" /> Cardboard
        </a>
        {hunt.name}
        <button type="button" className="btn ml-auto" onClick={toggleDrawer}>
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
        <div className="nav-link">Logged in as {window.LOGGED_IN_USER}</div>

        <div className="mt-auto" style={{ marginBottom: "36px" }}>
          <span
            style={{
              borderTop: "1px solid black",
              width: "100%",
              display: "inline-block",
            }}
            className="font-weight-bold nav-link"
          >
            Chat Settings
          </span>
          <div className="nav-link">
            <ChatVersionSelector />
          </div>
          <span
            style={{
              borderTop: "1px solid black",
              width: "100%",
              display: "inline-block",
            }}
            className="font-weight-bold nav-link"
          >
            Appearance
          </span>
          <div className="nav-link">
            <DarkModeToggle />
          </div>
        </div>
      </Drawer>
    </>
  );
};
