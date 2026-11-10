import React from "react";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";
import Drawer from "react-modern-drawer";
import { useTranslation } from "react-i18next";
import { DarkModeToggle } from "./DarkModeToggle";
import { ChatVersionSelector } from "./chatSelector";
import { LanguageSelector } from "./LanguageSelector";
import { IconMenu2 } from "@tabler/icons";
import "react-modern-drawer/dist/index.css";
import { useStore } from "./store";

const GoogleDriveIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="icon icon-tabler icons-tabler-outline icon-tabler-brand-google-drive"
  >
    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
    <path d="M12 10l-6 10l-3 -5l6 -10l3 5" />
    <path d="M9 15h12l-3 5h-12" />
    <path d="M15 15l-6 -10h6l6 10l-6 0" />
  </svg>
);

const ChartBarIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="icon icon-tabler icons-tabler-outline icon-tabler-chart-bar"
  >
    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
    <path d="M3 13a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -6" />
    <path d="M15 9a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -10" />
    <path d="M9 5a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -14" />
    <path d="M4 20h14" />
  </svg>
);

export const SiteHeader = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const hunt = useStore((state) => state.huntSlice.hunt);
  const { t } = useTranslation();

  const toggleDrawer = () => {
    setIsOpen((prevState) => !prevState);
  };

  const driveRedirect = hunt.has_drive ? (
    <OverlayTrigger
      placement="bottom"
      overlay={
        <Tooltip id="tooltip-gdrive">{t("google-drive-folder")}</Tooltip>
      }
    >
      <a className="btn" href="drive" aria-label={t("google-drive-folder")}>
        <GoogleDriveIcon />
      </a>
    </OverlayTrigger>
  ) : null;

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

        <div class="d-flex fw-bold text-center justify-content-end flex-nowrap flex-grow-1">
          <div className="text-nowrap">
            <OverlayTrigger
              placement="bottom"
              overlay={<Tooltip id="tooltip-stats">{t("stats")}</Tooltip>}
            >
              <a className="btn" href="stats" aria-label={t("stats")}>
                <ChartBarIcon />
              </a>
            </OverlayTrigger>
          </div>
          <div className="text-nowrap">{driveRedirect}</div>
        </div>

        <button type="button" className="btn ms-auto" onClick={toggleDrawer}>
          <IconMenu2 aria-label={t("expand-menu")} />
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
          {t("back-to-index")}
        </a>
        <a className="nav-link" href="/tools">
          {t("tools-and-references")}
        </a>
        <a className="nav-link" href="/accounts/logout/">
          {t("logout")}
        </a>
        <div style={{ padding: ".5rem 1rem" }}>
          {t("logged-in-as", {
            user: window.LOGGED_IN_USER,
          })}
        </div>

        <div
          className="mt-auto"
          style={{ padding: ".5rem 1rem", marginBottom: "36px" }}
        >
          <span
            style={{
              borderTop: "1px solid black",
              width: "100%",
              display: "inline-block",
              fontWeight: "bold",
              padding: ".5rem 1rem",
            }}
          >
            {t("language")}
          </span>
          <div style={{ padding: ".5rem 1rem" }}>
            <LanguageSelector />
          </div>

          <span
            style={{
              borderTop: "1px solid black",
              width: "100%",
              display: "inline-block",
              fontWeight: "bold",
            }}
          >
            {t("chat-settings")}
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
            {t("appearance")}
          </span>
          <div style={{ padding: ".5rem 1rem" }}>
            <DarkModeToggle />
          </div>
        </div>
      </Drawer>
    </>
  );
};
