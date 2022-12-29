import React from "react";
import Badge from "react-bootstrap/Badge";
import { useSelector, useDispatch } from "react-redux";
import { faEdit, faTrashAlt } from "@fortawesome/free-regular-svg-icons";
import { showModal } from "./modalSlice";
import ClickableIcon from "./ClickableIcon";
import { toggleCollapsed } from "./collapsedPuzzlesSlice";

const useToggleRowExpandedProps = (row) => {
  const dispatch = useDispatch();
  const originalProps = row.getToggleRowExpandedProps({
    style: {
      paddingLeft: `${row.depth * 2}rem`,
    },
  });

  return {
    ...originalProps,
    onClick: (e) => {
      dispatch(toggleCollapsed({ rowId: row.id }));
      return originalProps.onClick(e);
    },
  };
};

export default function NameCell({ row, value }) {
  const { id: huntId } = useSelector((state) => state.hunt);
  const props = useToggleRowExpandedProps(row);
  const dispatch = useDispatch();
  return (
    <>
      {row.canExpand ? (
        <span {...props}>
          {row.isExpanded ? "▼" : "▶"} <b>{value}</b>
        </span>
      ) : (
        <span style={{ paddingLeft: `${row.depth * 2}rem` }}>
          <b>{value}</b>
        </span>
      )}{" "}
      {row.values.is_meta ? (
        <>
          <Badge variant="dark">META</Badge>{" "}
        </>
      ) : null}
      <ClickableIcon
        icon={faEdit}
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
    </>
  );
}
