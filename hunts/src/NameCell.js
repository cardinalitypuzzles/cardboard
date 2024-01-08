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
            {nameText}
          </span>
        ) : (
          <span>{nameText}</span>
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
      <div>
        <TagCell row={row} />
      </div>
    </div>
  );
}
