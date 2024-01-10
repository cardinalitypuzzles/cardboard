import React from "react";
import { DarkModeToggle } from "./DarkModeToggle";
import Cookies from "js-cookie";
import Drawer from "react-modern-drawer";
import { ChatVersionSelector } from "./chatSelector";
import { useSelector, useDispatch } from "react-redux";
import { IconMenu2 } from "@tabler/icons";
import "react-modern-drawer/dist/index.css";
import { showAlert, hideAlert } from "./alertSlice";

export const SiteHeader = () => {
  const dispatch = useDispatch();

  const [isOpen, setIsOpen] = React.useState(false);
  const hunt = useSelector((state) => state.hunt);
  const toggleDrawer = () => {
    setIsOpen((prevState) => !prevState);
  };

  let syncDiscordAndCardboardTags = (huntSlug) => {
    const tagsApiUrl = `sync_discord_roles`;
    fetch(tagsApiUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Content-Type": "application/json",
      },
    }).then(() => {
      dispatch(
        showAlert({
          variant: "info",
          text: "Discord roles updated successfully.",
        })
      );
      setIsOpen(false);
    });
  };

  return (
    <>
      <nav
        className="navbar navbar-expand-lg navbar-themed"
        style={{ marginBottom: "5px" }}
      >
        <a className="navbar-brand" href="/">
          <img height="40" src="/static/favicon.ico" alt="" />{" "}
          {window.APP_SHORT_TITLE}
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
      </Drawer>
    </>
  );
};
