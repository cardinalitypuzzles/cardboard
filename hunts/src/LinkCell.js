import React from "react";
import { useSelector } from "react-redux";
import { CHAT_VERSION_OPTIONS, getChatVersion } from "./chatSlice";
import { IconLink } from "./ClickableIcon";
import { CHAT_PLATFORM } from "./constants";
import { SHEET_REDIRECT_BASE } from "./constants";
import { faPuzzlePiece } from "@fortawesome/free-solid-svg-icons";

const createSheetLink = (puzzle) => {
  return `${SHEET_REDIRECT_BASE}/${puzzle.id}`;
};

const hasDiscordLink = (puzzle) => {
  return puzzle.chat_room && puzzle.chat_room.text_channel_url.length > 0;
};

const createDiscordLink = (puzzle, chatVersion) => {
  if (!hasDiscordLink(puzzle)) {
    return "";
  }

  if (chatVersion === CHAT_VERSION_OPTIONS.APP) {
    return puzzle.chat_room.text_channel_url.replace("https", CHAT_PLATFORM);
  }

  return puzzle.chat_room.text_channel_url;
};

const DiscordSvg = () => {
  return (
    <svg
      width="24px"
      height="24px"
      viewBox="-1 0 20 20"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M15.45,0 C16.5684694,0 17.4812026,0.901320283 17.4997134,2.02517151 L17.5,2.06 L17.5,20 L15.35,18.1 L14.14,16.98 L12.86,15.79 L13.39,17.64 L2.05,17.64 C0.931530612,17.64 0.0187973761,16.7386797 0.000286625896,15.6148285 L0,15.58 L0,2.06 C0,0.931632653 0.901320283,0.0187984173 2.01547452,0.00028663652 L2.05,0 L15.45,0 Z M7.32,4.78 L7.22,4.6599169 L7.1630624,4.66059412 C6.890192,4.66871965 5.6772,4.7596 4.41,5.71 L4.36156128,5.802081 C4.110624,6.291581 2.97,8.6742 2.97,11.54 L2.99079837,11.5731719 C3.132297,11.789822 4.0089,12.9963 6.02,13.06 L6.31452473,12.6987136 C6.43107266,12.5548097 6.56647059,12.3864706 6.69,12.23 C5.5242617,11.8811964 5.02413637,11.1785226 4.94987673,11.0655003 L4.94,11.05 L4.98113281,11.0774219 C5.02625,11.1067188 5.1075,11.1575 5.22,11.22 C5.23,11.23 5.24,11.24 5.26,11.25 C5.29,11.27 5.32,11.28 5.35,11.3 C5.6,11.44 5.85,11.55 6.08,11.64 C6.49,11.8 6.98,11.96 7.55,12.07 C8.27857143,12.206 9.12982041,12.2570694 10.0579114,12.0948686 L10.14,12.08 C10.61,12 11.09,11.86 11.59,11.65 C11.94,11.52 12.33,11.33 12.74,11.06 L12.7236045,11.0849198 C12.6278835,11.2248395 12.1044828,11.9182759 10.93,12.25 L11.0953826,12.4572606 C11.347936,12.770868 11.59,13.06 11.59,13.06 C13.8,12.99 14.65,11.54 14.65,11.54 C14.65,8.32 13.21,5.71 13.21,5.71 C11.9716,4.7812 10.784972,4.67329454 10.4769888,4.66128549 L10.4,4.6599169 L10.26,4.82 C11.7675403,5.28112997 12.5594623,5.92313048 12.7194499,6.06258405 L12.75,6.09 C11.71,5.52 10.69,5.24 9.74,5.13 C9.02,5.05 8.33,5.07 7.72,5.15 C7.66,5.15 7.61,5.16 7.55,5.17 L7.493785,5.17528 C7.11445,5.21385 6.2965,5.3535 5.28,5.8 L5.13470143,5.86775227 C4.9530442,5.9537305 4.82068394,6.02127593 4.74962341,6.05838585 L4.69,6.09 C4.69,6.09 5.503483,5.315721 7.26629086,4.79567994 L7.32,4.78 Z M6.94,8.39 C7.51,8.39 7.97,8.89 7.96,9.5 C7.96,10.11 7.51,10.61 6.94,10.61 C6.38,10.61 5.92,10.11 5.92,9.5 C5.92,8.89 6.37,8.39 6.94,8.39 Z M10.59,8.39 C11.16,8.39 11.61,8.89 11.61,9.5 C11.61,10.11 11.16,10.61 10.59,10.61 C10.03,10.61 9.57,10.11 9.57,9.5 C9.57,8.89 10.02,8.39 10.59,8.39 Z" />
    </svg>
  );
};

const SheetsSvg = () => {
  return (
    <svg
      width="24px"
      height="24px"
      viewBox="0 0 24 24"
      role="img"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M4.908 0c-.873 0-1.635.764-1.635 1.637v20.726c0 .873.762 1.637 1.635 1.637h14.184c.873 0 1.635-.764 1.635-1.637V7.045h-4.909a2.157 2.157 0 0 1-2.136-2.137V0H4.908zm9.774.5v4.408c0 .581.555 1.137 1.136 1.137h4.409L14.682.5zM7.637 11.781h8.726v7.856H7.637V11.78zm1.09 1.092v1.309h2.728v-1.309H8.727zm3.818 0v1.309h2.728v-1.309h-2.728zm-3.818 2.182v1.308h2.728v-1.308H8.727zm3.818 0v1.308h2.728v-1.308h-2.728zm-3.818 2.181v1.309h2.728v-1.309H8.727zm3.818 0v1.309h2.728v-1.309h-2.728z" />
    </svg>
  );
};

const SvgLink = ({ children, url, style }) => {
  return (
    <a href={url} target="_blank" style={style} className="text-muted">
      {children}
    </a>
  );
};

export const LinkCell = ({ row }) => {
  const puzzle = row.original;
  const puzzleLink = puzzle.url;

  const hasSheet = puzzle.has_sheet;
  const sheetLink = createSheetLink(puzzle);

  const chatVersion = useSelector(getChatVersion);
  const hasDiscord = hasDiscordLink(puzzle);
  const discordLink = createDiscordLink(puzzle, chatVersion);

  return (
    <>
      <IconLink
        icon={faPuzzlePiece}
        url={puzzleLink}
        size="lg"
        style={{
          margin: "0 5px",
        }}
      ></IconLink>

      {hasSheet ? (
        <SvgLink
          url={sheetLink}
          style={{
            margin: "0 5px",
            fill: "currentColor",
          }}
        >
          <SheetsSvg />
        </SvgLink>
      ) : null}

      {hasDiscord ? (
        <SvgLink
          url={discordLink}
          style={{
            margin: "0 5px",
            fill: "currentColor",
          }}
        >
          <DiscordSvg />
        </SvgLink>
      ) : null}
    </>
  );
};
