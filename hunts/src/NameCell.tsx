import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { faWrench, faTag } from "@fortawesome/free-solid-svg-icons";
import { showModal } from "./modalSlice";
import TagCell from "./TagCell";
import ClickableIcon from "./ClickableIcon";
import { toggleCollapsed } from "./collapsedPuzzlesSlice";
import { IconChevronDown, IconChevronRight } from "@tabler/icons";
import { faCircle } from "@fortawesome/free-solid-svg-icons";

import {
  Hunt,
  Puzzle,
  Row,
  SafeBadge,
  SafeFontAwesomeIcon,
  SafeOverlayTrigger,
  SafePopover,
  SafeReactTimeAgo,
} from "./types";
import { RootState } from "./store";

const getColor = (min_since_edit: number) => {
  if (min_since_edit <= 5) {
    return "text-success";
  } else if (min_since_edit <= 30) {
    return "text-warning";
  } else {
    return "text-danger";
  }
};

const LastActive = ({ last_edited_on }: { last_edited_on: string }) => {
  const last_edited_date = new Date(Date.parse(last_edited_on));
  const min_since_edit =
    (Date.now() - last_edited_date.getTime()) / (1000 * 60);
  const editedOnPopOver = (
    <SafePopover className="bootstrap">
      <SafePopover.Content>
        Last active <SafeReactTimeAgo date={last_edited_date} locale="en-US" />
      </SafePopover.Content>
    </SafePopover>
  );
  return (
    <>
      <SafeOverlayTrigger
        trigger={["hover", "focus"]}
        placement="right"
        overlay={editedOnPopOver}
      >
        <SafeFontAwesomeIcon
          className={getColor(min_since_edit)}
          style={{ verticalAlign: "-0.125em" }}
          icon={faCircle}
        />
      </SafeOverlayTrigger>
    </>
  );
};

const PuzzleTitle = ({
  name,
  last_edited_on,
  is_solved,
}: {
  name: string;
  last_edited_on: string;
  is_solved: boolean;
}) => {
  return (
    <>
      {last_edited_on && !is_solved && (
        <>
          <LastActive last_edited_on={last_edited_on} />{" "}
        </>
      )}
      <b>{name}</b>
    </>
  );
};

const useToggleRowExpandedProps = (row: Row<Puzzle>) => {
  const dispatch = useDispatch();
  const originalProps = row.getToggleRowExpandedProps({});

  return {
    ...originalProps,
    onClick: (e: MouseEvent) => {
      dispatch(toggleCollapsed({ rowId: row.id, huntId: CURRENT_HUNT_ID }));
      return originalProps.onClick(e);
    },
  };
};

export default function NameCell({
  row,
  value,
}: {
  row: Row<Puzzle>;
  value: string;
}) {
  const { id: huntId } = useSelector<RootState, Hunt>((state) => state.hunt);
  const [uiHovered, setUiHovered] = React.useState(false);
  const toggleRowExpandedProps = useToggleRowExpandedProps(row);
  const dispatch = useDispatch();

  const nameText = (
    <span>
      <b>{value}</b>
    </span>
  );

  return (
    <div
      style={{
        paddingLeft: `${row.depth * 2}rem`,
      }}
    >
      <div
        onMouseEnter={() => {
          setUiHovered(true);
        }}
        onMouseLeave={() => {
          setUiHovered(false);
        }}
        style={{
          marginBottom: "3px",
        }}
      >
        {row.canExpand ? (
          <span {...toggleRowExpandedProps}>
            {row.isExpanded ? <IconChevronDown /> : <IconChevronRight />}
            <PuzzleTitle
              name={value}
              last_edited_on={row.values.last_edited_on}
              is_solved={row.values.status === "SOLVED"}
            ></PuzzleTitle>
          </span>
        ) : (
          <span>
            <PuzzleTitle
              name={value}
              last_edited_on={row.values.last_edited_on}
              is_solved={row.values.status === "SOLVED"}
            ></PuzzleTitle>
          </span>
        )}{" "}
        {row.values.is_meta ? (
          <>
            <SafeBadge variant="dark">META</SafeBadge>{" "}
          </>
        ) : null}
        <div
          style={{
            display: "inline-block",
            visibility: uiHovered ? "visible" : "hidden",
          }}
        >
          <ClickableIcon
            icon={faWrench}
            onClick={() =>
              dispatch(
                showModal({
                  type: "EDIT_PUZZLE",
                  props: {
                    huntId,
                    puzzleId: row.values.id,
                    name: row.values.name,
                    url: row.values.url,
                    isMeta: row.values.is_meta,
                    hasChannels: !!row.original.chat_room?.text_channel_url,
                  },
                })
              )
            }
          />{" "}
          <ClickableIcon
            icon={faTag}
            onClick={() =>
              dispatch(
                showModal({
                  type: "EDIT_TAGS",
                  props: {
                    huntId,
                    puzzleId: row.values.id,
                    puzzleName: row.values.name,
                  },
                })
              )
            }
          />{" "}
          <ClickableIcon
            icon={faTrashAlt}
            onClick={() =>
              dispatch(
                showModal({
                  type: "DELETE_PUZZLE",
                  props: {
                    huntId,
                    puzzleId: row.values.id,
                    puzzleName: value,
                  },
                })
              )
            }
          />
        </div>
      </div>
    </div>
  );
}
