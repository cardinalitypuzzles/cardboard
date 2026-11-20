import React from "react";
import Cookies from "js-cookie";
import Button from "react-bootstrap/Button";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";
import Drawer from "react-modern-drawer";
import { useTranslation } from "react-i18next";
import { DarkModeToggle } from "./DarkModeToggle";
import { ChatVersionSelector } from "./chatSelector";
import { LanguageSelector } from "./LanguageSelector";
import GlobalFilter from "./GlobalFilter";
import { SolvedStateFilter } from "./solveStateFilter";
import { StatsDrawer } from "./StatsDrawer";
import { IconMenu2, IconPlus } from "@tabler/icons";
import "react-modern-drawer/dist/index.css";
import { useStore } from "./store";
import type { HuntId } from "./types";

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

const ChartLineIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
  >
    <g
      fill="none"
      stroke="currentColor"
      strokeLinecap="square"
      strokeMiterlimit="3.5"
      strokeWidth="1.5"
    >
      <path d="M3.5 3v17.5H21" />
      <path d="m6.5 16l4-5l3.5 3l5-7.5" />
    </g>
  </svg>
);

export const SiteHeader = ({ huntId }: { huntId?: HuntId }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [isStatsOpen, setIsStatsOpen] = React.useState(false);
  const [headerHeight, setHeaderHeight] = React.useState(44);
  const navRef = React.useRef<HTMLElement>(null);
  const hunt = useStore((state) => state.huntSlice.hunt);
  const modal = useStore((state) => state.modalSlice);
  const { t } = useTranslation();

  React.useLayoutEffect(() => {
    const nav = navRef.current;
    if (!nav) return;
    const updateHeight = () => setHeaderHeight(nav.offsetHeight);
    updateHeight();
    if (typeof ResizeObserver !== "undefined") {
      const observer = new ResizeObserver(updateHeight);
      observer.observe(nav);
      return () => observer.disconnect();
    }
    window.addEventListener("resize", updateHeight);
    return () => window.removeEventListener("resize", updateHeight);
  }, []);

  const toggleDrawer = () => {
    setIsOpen((prevState) => {
      if (!prevState) {
        setIsStatsOpen(false);
      }
      return !prevState;
    });
  };

  const toggleStatsDrawer = () => {
    setIsStatsOpen((prevState) => {
      if (!prevState) {
        setIsOpen(false);
      }
      return !prevState;
    });
  };

  const driveRedirect = hunt.has_drive ? (
    <OverlayTrigger
      placement="bottom"
      overlay={
        <Tooltip id="tooltip-gdrive">{t("google-drive-folder")}</Tooltip>
      }
    >
      <a
        className="btn btn-sm"
        href="drive"
        aria-label={t("google-drive-folder")}
      >
        <GoogleDriveIcon />
      </a>
    </OverlayTrigger>
  ) : null;

  return (
    <>
      <nav
        ref={navRef}
        className="navbar navbar-expand-lg navbar-themed fixed-top py-1 border-bottom cb-masthead"
      >
        <div className="cb-shell d-flex align-items-center flex-wrap gap-2">
          <div
            className="d-flex align-items-center text-nowrap"
            style={{ marginRight: "3rem" }}
          >
            <a href="/" className="me-2 d-flex align-items-center">
              <img width="26" src={`/static/${window.FAVICON}`} alt="" />
            </a>
            <a
              className="navbar-brand py-0 me-0"
              href="/"
              style={{ fontSize: "1.05rem" }}
            >
              {window.APP_SHORT_TITLE}
            </a>
            {hunt.name && (
              <span
                className="d-inline-flex align-items-center text-body-secondary ms-2"
                style={{ fontSize: "0.82rem", opacity: 0.78 }}
              >
                <span>/</span>
                <span className="ms-2" style={{ paddingTop: "2px" }}>
                  {hunt.name}
                </span>
              </span>
            )}
          </div>

          <div className="d-flex align-items-center justify-content-between flex-grow-1 flex-wrap gap-2">
            <div className="d-flex align-items-center gap-2 flex-wrap">
              <GlobalFilter />
              <div className="d-flex align-items-center text-nowrap">
                <SolvedStateFilter />
              </div>
            </div>

            <div className="d-flex align-items-center flex-nowrap ms-auto">
              <Button
                variant="primary"
                size="sm"
                className="d-inline-flex align-items-center gap-1 text-nowrap btn-add-puzzle"
                style={{ marginRight: "2.5rem" }}
                onClick={() =>
                  modal.showModal({
                    type: "ADD_PUZZLE",
                    props: {
                      huntId: huntId ?? hunt.id ?? CURRENT_HUNT_ID,
                    },
                  })
                }
              >
                <IconPlus size={16} />
                {t("add-puzzle")}
              </Button>

              <div className="d-flex fw-bold text-center align-items-center flex-nowrap">
                <div className="text-nowrap">{driveRedirect}</div>
                <div className="text-nowrap">
                  <OverlayTrigger
                    placement="bottom"
                    overlay={<Tooltip id="tooltip-stats">{t("stats")}</Tooltip>}
                  >
                    <a
                      className="btn btn-sm"
                      href="#stats"
                      role="button"
                      onClick={(e) => {
                        e.preventDefault();
                        toggleStatsDrawer();
                      }}
                      aria-label={t("stats")}
                    >
                      <ChartLineIcon />
                    </a>
                  </OverlayTrigger>
                </div>
                <button
                  type="button"
                  className="btn btn-sm"
                  onClick={toggleDrawer}
                >
                  <IconMenu2 aria-label={t("expand-menu")} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>
      <div style={{ height: `${headerHeight}px`, marginBottom: "5px" }} />
      <Drawer
        open={isOpen}
        onClose={toggleDrawer}
        direction="right"
        zIndex={1040}
        customIdSuffix="settings"
        className="navbar-themed"
        style={{
          display: "flex",
          flexDirection: "column",
        }}
      >
        {hunt.is_admin && (
          <a className="nav-link" href={`/hunts/${hunt.slug}/edit`}>
            {t("hunt-settings")}
          </a>
        )}
        <a className="nav-link" href="/hunts">
          {t("back-to-index")}
        </a>
        <a className="nav-link" href="/tools">
          {t("tools-and-references")}
        </a>
        <form method="post" action="/accounts/logout/">
          <input
            type="hidden"
            name="csrfmiddlewaretoken"
            value={Cookies.get("csrftoken") ?? ""}
          />
          <button type="submit" className="nav-link nav-link-button">
            {t("logout")}
          </button>
        </form>
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
      <StatsDrawer open={isStatsOpen} onClose={() => setIsStatsOpen(false)} />
    </>
  );
};
