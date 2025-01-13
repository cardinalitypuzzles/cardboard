import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { CHAT_VERSION_OPTIONS, getChatVersion } from "./chatSlice";
import { IconLink } from "./ClickableIcon";
import { CHAT_PLATFORM, SHEET_REDIRECT_BASE } from "./constants";
import { updatePuzzle } from "./puzzlesSlice";
import { faPuzzlePiece } from "@fortawesome/free-solid-svg-icons";

import type { Dispatch } from "./store";
import type { Puzzle, Row } from "./types";

const createSheetLink = (puzzle: Puzzle) => {
  return `${SHEET_REDIRECT_BASE}/${puzzle.id}`;
};

const hasDiscordLink = (puzzle: Puzzle) => {
  return !!puzzle.chat_room?.text_channel_url;
};

const createDiscordLink = (puzzle: Puzzle, chatVersion: number) => {
  if (!hasDiscordLink(puzzle)) {
    return "";
  }

  if (chatVersion === CHAT_VERSION_OPTIONS.APP) {
    return puzzle.chat_room!.text_channel_url!.replace("https", CHAT_PLATFORM);
  }

  return puzzle.chat_room!.text_channel_url!;
};

const BlurpleDiscordSvg = () => <DiscordSvg fillColor="#5865F2" />;
const LightBlurpleDiscordSvg = () => <DiscordSvg fillColor="#CCD0FB" />;
const PulsingBlurpleDiscordSvg = () => {
  return (
    <>
      <style>{`
        .custom-discord-pulse > svg > * {
          animation: pulse 1s infinite;
          -webkit-animation: pulse 1s infinite;
        }
        @keyframes pulse {
          0%   { fill: #5865F2 }
          50%  { fill: #CCD0FB }
          100% { fill: #5865F2 }
        }
        @-webkit-keyframes pulse {
          0%   { fill: #5865F2 }
          50%  { fill: #CCD0FB }
          100% { fill: #5865F2 }
        }
      `}</style>
      <span
        className="custom-discord-pulse"
        style={{
          margin: "0 5px",
          display: "inline-block",
        }}
        title="loading"
      >
        <DiscordSvg />
      </span>
    </>
  );
};

const DiscordSvg = ({ fillColor } : { fillColor?: string }) => {
  return (
    <svg
      width="26px"
      height="24px"
      viewBox="0 -28.5 256 256"
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid"
    >
      <g>
        <path
          d="M216.856339,16.5966031 C200.285002,8.84328665 182.566144,3.2084988 164.041564,0 C161.766523,4.11318106 159.108624,9.64549908 157.276099,14.0464379 C137.583995,11.0849896 118.072967,11.0849896 98.7430163,14.0464379 C96.9108417,9.64549908 94.1925838,4.11318106 91.8971895,0 C73.3526068,3.2084988 55.6133949,8.86399117 39.0420583,16.6376612 C5.61752293,67.146514 -3.4433191,116.400813 1.08711069,164.955721 C23.2560196,181.510915 44.7403634,191.567697 65.8621325,198.148576 C71.0772151,190.971126 75.7283628,183.341335 79.7352139,175.300261 C72.104019,172.400575 64.7949724,168.822202 57.8887866,164.667963 C59.7209612,163.310589 61.5131304,161.891452 63.2445898,160.431257 C105.36741,180.133187 151.134928,180.133187 192.754523,160.431257 C194.506336,161.891452 196.298154,163.310589 198.110326,164.667963 C191.183787,168.842556 183.854737,172.420929 176.223542,175.320965 C180.230393,183.341335 184.861538,190.991831 190.096624,198.16893 C211.238746,191.588051 232.743023,181.531619 254.911949,164.955721 C260.227747,108.668201 245.831087,59.8662432 216.856339,16.5966031 Z M85.4738752,135.09489 C72.8290281,135.09489 62.4592217,123.290155 62.4592217,108.914901 C62.4592217,94.5396472 72.607595,82.7145587 85.4738752,82.7145587 C98.3405064,82.7145587 108.709962,94.5189427 108.488529,108.914901 C108.508531,123.290155 98.3405064,135.09489 85.4738752,135.09489 Z M170.525237,135.09489 C157.88039,135.09489 147.510584,123.290155 147.510584,108.914901 C147.510584,94.5396472 157.658606,82.7145587 170.525237,82.7145587 C183.391518,82.7145587 193.761324,94.5189427 193.539891,108.914901 C193.539891,123.290155 183.391518,135.09489 170.525237,135.09489 Z"
          fill={fillColor}
          fillRule="nonzero"
          stroke="#000"
          strokeWidth="1"
        />
      </g>
    </svg>
  );
};

const GreenSheetsSvg = () => {
  return (
    <svg
      width="24px"
      height="24px"
      version="1.1"
      id="Layer_1"
      xmlns="http://www.w3.org/2000/svg"
      x="0px"
      y="0px"
      viewBox="0 0 512 512"
    >
      <path
        style={{ fill: "#12B347" }}
        d="M456.348,495.304c0,9.217-7.479,16.696-16.696,16.696H72.348c-9.217,0-16.696-7.479-16.696-16.696
	V16.696C55.652,7.479,63.131,0,72.348,0h233.739c4.424,0,8.674,1.761,11.804,4.892l133.565,133.565
	c3.131,3.13,4.892,7.379,4.892,11.804V495.304z"
      />
      <path
        style={{ fill: "#0F993E" }}
        d="M456.348,495.304V150.278c0-4.437-1.766-8.691-4.909-11.822L317.389,4.871
	C314.258,1.752,310.019,0,305.601,0H256v512h183.652C448.873,512,456.348,504.525,456.348,495.304z"
      />
      <path
        style={{ fill: "#12B347" }}
        d="M451.459,138.459L317.891,4.892C314.76,1.76,310.511,0,306.082,0h-16.691l0.001,150.261
	c0,9.22,7.475,16.696,16.696,16.696h150.26v-16.696C456.348,145.834,454.589,141.589,451.459,138.459z"
      />
      <path
        style={{ fill: "#FFFFFF" }}
        d="M372.87,211.478H139.13c-9.217,0-16.696,7.479-16.696,16.696v200.348
	c0,9.217,7.479,16.696,16.696,16.696H372.87c9.217,0,16.696-7.479,16.696-16.696V228.174
	C389.565,218.957,382.087,211.478,372.87,211.478z M155.826,311.652h66.783v33.391h-66.783V311.652z M256,311.652h100.174v33.391
	H256V311.652z M356.174,278.261H256V244.87h100.174V278.261z M222.609,244.87v33.391h-66.783V244.87H222.609z M155.826,378.435
	h66.783v33.391h-66.783V378.435z M256,411.826v-33.391h100.174v33.391H256z"
      />
      <path
        style={{ fill: "#E6F3FF" }}
        d="M372.87,211.478H256v33.391h100.174v33.391H256v33.391h100.174v33.391H256v33.391h100.174v33.391H256
	v33.391h116.87c9.22,0,16.696-7.475,16.696-16.696V228.174C389.565,218.953,382.09,211.478,372.87,211.478z"
      />
    </svg>
  );
};

const SvgLink = ({
  children,
  url,
  style,
}: {
  children: React.ReactNode;
  url: string;
  style: React.CSSProperties;
}) => {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      style={style}
      className="text-muted"
    >
      {children}
    </a>
  );
};

export const LinkCell = ({ row }: { row: Row<Puzzle> }) => {
  const puzzle = row.original;
  const puzzleLink = puzzle.url;

  const hasSheet = puzzle.has_sheet;
  const sheetLink = createSheetLink(puzzle);

  const chatVersion = useSelector(getChatVersion);
  const hasDiscord = hasDiscordLink(puzzle);
  const discordLink = createDiscordLink(puzzle, chatVersion);

  const dispatch = useDispatch<Dispatch>();
  const [loadingDiscord, setLoadingDiscord] = React.useState(false);

  const createDiscordChannels = () => {
    setLoadingDiscord(true);
    dispatch(
      updatePuzzle({
        huntId: puzzle.hunt_id,
        id: puzzle.id,
        body: {
          create_channels: true,
        },
      })
    );
  };

  return (
    <div
      style={{
        width: "110px",
      }}
    >
      <IconLink
        icon={faPuzzlePiece}
        url={puzzleLink}
        size="lg"
        style={{
          margin: "0 5px",
          display: "inline-block",
        }}
      />

      {hasSheet ? (
        <SvgLink
          url={sheetLink}
          style={{
            margin: "0 5px",
            fill: "currentColor",
            display: "inline-block",
          }}
        >
          <GreenSheetsSvg />
        </SvgLink>
      ) : null}

      {hasDiscord ? (
        <SvgLink
          url={discordLink}
          style={{
            margin: "0 5px",
            display: "inline-block",
          }}
        >
          <BlurpleDiscordSvg />
        </SvgLink>
      ) : loadingDiscord ? (
        <PulsingBlurpleDiscordSvg />
      ) : (
        <a
          onClick={createDiscordChannels}
          className="text-muted"
          style={{
            margin: "0 5px",
            display: "inline-block",
          }}
          title="Create channels"
        >
          <LightBlurpleDiscordSvg />
        </a>
      )}
    </div>
  );
};
