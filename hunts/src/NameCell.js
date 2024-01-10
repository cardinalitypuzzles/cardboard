import React from "react";
import Badge from "react-bootstrap/Badge";
import { useSelector, useDispatch } from "react-redux";
import { faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { faWrench, faTag } from "@fortawesome/free-solid-svg-icons";
import { showModal } from "./modalSlice";
import TagCell from "./TagCell";
import ClickableIcon from "./ClickableIcon";
import { toggleCollapsed } from "./collapsedPuzzlesSlice";
import { IconChevronDown, IconChevronRight } from "@tabler/icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircle } from "@fortawesome/free-solid-svg-icons";
import { OverlayTrigger, Popover } from "react-bootstrap";
import ReactTimeAgo from "react-time-ago";

const getColor = (min_since_edit) => {
  if (min_since_edit <= 5) {
    return "text-success";
  } else if (min_since_edit <= 30) {
    return "text-warning";
  } else {
    return "text-danger";
  }
};

const LastActive = ({ last_edited_on }) => {
  const last_edited_date = new Date(Date.parse(last_edited_on));
  const min_since_edit = (Date.now() - last_edited_date) / (1000 * 60);
  const editedOnPopOver = (
    <Popover className="bootstrap">
      <Popover.Content>
        Last active <ReactTimeAgo date={last_edited_date} locale="en-US" />
      </Popover.Content>
    </Popover>
  );
  return (
    <>
      <OverlayTrigger
        trigger={["hover", "focus"]}
        placement="right"
        overlay={editedOnPopOver}
      >
        <FontAwesomeIcon
          className={getColor(min_since_edit)}
          style={{ verticalAlign: "-0.125em" }}
          icon={faCircle}
        />
      </OverlayTrigger>
    </>
  );
};

const PuzzleTitle = ({ name, last_edited_on }) => {
  return (
    <>
      {last_edited_on && <LastActive last_edited_on={last_edited_on} />}{" "}
      <b>{name}</b>
    </>
  );
};

const useToggleRowExpandedProps = (row) => {
  const dispatch = useDispatch();
  const originalProps = row.getToggleRowExpandedProps({});

  return {
    ...originalProps,
    onClick: (e) => {
      dispatch(toggleCollapsed({ rowId: row.id, huntId: CURRENT_HUNT_ID }));
      return originalProps.onClick(e);
    },
  };
};

export default function NameCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
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
            ></PuzzleTitle>
          </span>
        ) : (
          <span>
            <PuzzleTitle
              name={value}
              last_edited_on={row.values.last_edited_on}
            ></PuzzleTitle>
          </span>
        )}{" "}
        {row.values.is_meta ? (
          <>
            <Badge variant="dark">META</Badge>{" "}
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
