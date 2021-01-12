import React from "react";
import PropTypes from "prop-types";
import { useSelector, useDispatch } from "react-redux";
import { fetchPuzzles, selectPuzzleTableData } from "./puzzlesSlice";
import { fetchHunt } from "./huntSlice";
import { showModal, hideModal } from "./modalSlice";
import { hideAlert } from "./alertSlice";
import { PuzzleTable } from "./puzzle-table";
import AnswerCell from "./AnswerCell";
import NameCell from "./NameCell";
import HuntViewHeader from "./HuntViewHeader";
import GlobalFilter from "./GlobalFilter";
import StatusCell from "./StatusCell";
import DeleteAnswerModal from "./DeleteAnswerModal";
import TagCell from "./TagCell";
import DeletePuzzleModal from "./DeletePuzzleModal";
import EditAnswerModal from "./EditAnswerModal";
import EditPuzzleModal from "./EditPuzzleModal";
import AddPuzzleModal from "./AddPuzzleModal";
import SubmitAnswerModal from "./SubmitAnswerModal";
import EditPuzzleTagsModal from "./EditPuzzleTagsModal";
import useInterval from "@use-it/interval";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";
import Modal from "react-bootstrap/Modal";
import Alert from "react-bootstrap/Alert";
import { SOLVE_STATE_FILTER_OPTIONS } from "./solveStateFilter";
import { SHEET_REDIRECT_BASE } from "./constants";
import { filterWithTagToggled } from "./tagFilter";
import TagPill from "./TagPill";

const MODAL_COMPONENTS = {
  DELETE_PUZZLE: DeletePuzzleModal,
  EDIT_PUZZLE: EditPuzzleModal,
  ADD_PUZZLE: AddPuzzleModal,
  SUBMIT_ANSWER: SubmitAnswerModal,
  DELETE_ANSWER: DeleteAnswerModal,
  EDIT_ANSWER: EditAnswerModal,
  EDIT_TAGS: EditPuzzleTagsModal,
};

const TABLE_COLUMNS = [
  {
    Header: "Name",
    accessor: "name",
    Cell: NameCell,
  },
  {
    Header: "Answer",
    accessor: (row) => row.guesses.map(({ text }) => text).join(" "),
    Cell: AnswerCell,
    id: "answer",
  },
  {
    Header: "Status",
    accessor: "status",
    Cell: StatusCell,
    filter: "solvedFilter",
  },
  {
    Header: "Puzzle",
    accessor: "url",
    Cell: ({ row, value }) => (
      <a href={value} target="_blank">
        Puzzle
      </a>
    ),
  },
  {
    Header: "Sheet",
    accessor: "has_sheet",
    Cell: ({ row, value }) =>
      value ? (
        <a href={`${SHEET_REDIRECT_BASE}/${row.original.id}`} target="_blank">
          Sheet
        </a>
      ) : null,
  },
  {
    Header: "Chat",
    accessor: "chat_room",
    Cell: ({ row, value }) =>
      row.original.chat_room ? (
        <>
          <a href={row.original.chat_room.text_channel_url} target="_blank">
            Text
          </a>
        </>
      ) : null,
  },
  {
    Header: "Tags/Metas",
    id: "tags",
    accessor: (row) => row.tags.map(({ name }) => name).join(" "),
    Cell: TagCell,
    filter: "tagsFilter",
  },
  {
    accessor: "is_meta",
    id: "is_meta",
  },
  {
    accessor: "id",
    id: "id",
  },
];

export const HuntViewMain = (props) => {
  const tableData = useSelector(selectPuzzleTableData);
  const modal = useSelector((state) => state.modal);
  const hunt = useSelector((state) => state.hunt);
  const alert = useSelector((state) => state.alert);
  const [filter, setFilter] = React.useState("");
  const [filterSolved, setFilterSolved] = React.useState(
    SOLVE_STATE_FILTER_OPTIONS.ALL
  );
  let [filterTags, setFilterTags] = React.useState([]);
  const toggleTagInFilter = (tag) => {
    setFilterTags(filterWithTagToggled(filterTags, tag));
  };
  const dispatch = useDispatch();

  const updatePuzzleData = () => {
    dispatch(fetchPuzzles(props.huntId));
  };

  useInterval(updatePuzzleData, 10 * 1000);

  const ModalComponent = MODAL_COMPONENTS[modal.type];
  React.useEffect(() => {
    dispatch(fetchHunt(props.huntId));
    updatePuzzleData();
  }, [props.huntId]);

  React.useEffect(() => {
    if (alert.show) {
      const timer = setTimeout(() => dispatch(hideAlert()), 8 * 1000);
      return () => clearTimeout(timer);
    }
  }, [alert.id]);

  return (
    <div
      style={{
        margin: "0 20px",
      }}
    >
      <Alert
        dismissible
        variant={alert.variant}
        show={alert.show}
        onClose={() => dispatch(hideAlert())}
      >
        {alert.text}
      </Alert>
      <HuntViewHeader hunt={hunt} />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          padding: "2px",
          alignItems: "center",
        }}
      >
        <div>
          <GlobalFilter globalFilter={filter} setGlobalFilter={setFilter} />
          <span>Show:</span>
          <label>
            <input
              style={{ margin: "0 5px 0 10px" }}
              type="radio"
              checked={filterSolved === SOLVE_STATE_FILTER_OPTIONS.ALL}
              onChange={(evt) => {
                if (evt.target.checked) {
                  setFilterSolved(SOLVE_STATE_FILTER_OPTIONS.ALL);
                }
              }}
            ></input>
            All
          </label>
          <label>
            <input
              style={{ margin: "0 5px 0 10px" }}
              type="radio"
              checked={
                filterSolved === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED ||
                filterSolved ===
                  SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
              }
              onChange={(evt) => {
                if (evt.target.checked) {
                  setFilterSolved(SOLVE_STATE_FILTER_OPTIONS.UNSOLVED);
                }
              }}
            ></input>
            Unsolved
          </label>
          {(filterSolved === SOLVE_STATE_FILTER_OPTIONS.UNSOLVED ||
            filterSolved ===
              SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS) && (
            <label>
              <input
                style={{ margin: "0 5px 0 10px" }}
                type="checkbox"
                checked={
                  filterSolved ===
                  SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
                }
                onChange={(evt) => {
                  if (evt.target.checked) {
                    setFilterSolved(
                      SOLVE_STATE_FILTER_OPTIONS.UNSOLVED_WITH_SOLVED_METAS
                    );
                  } else {
                    setFilterSolved(SOLVE_STATE_FILTER_OPTIONS.UNSOLVED);
                  }
                }}
              ></input>
              Include unsolved w/ solved metas
            </label>
          )}
        </div>
        <div>
          {filterTags.length > 0 ? "Viewing puzzles with tags: " : ""}
          {filterTags.map(({ name, color, id }) => {
            // This use of toggleTagInFilter will always delete the tag, never add it.
            return (
              <TagPill
                name={name}
                color={color}
                id={id}
                puzzleId={null}
                key={name}
                onDelete={function () {
                  toggleTagInFilter({ name, color, id });
                }}
              />
            );
          })}
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={() =>
            dispatch(
              showModal({
                type: "ADD_PUZZLE",
                props: {
                  huntId: props.huntId,
                },
              })
            )
          }
        >
          Add Puzzle
        </Button>
      </div>
      <PuzzleTable
        columns={TABLE_COLUMNS}
        data={tableData}
        filter={filter}
        filterSolved={filterSolved}
        filterTags={filterTags}
        toggleTagInFilter={toggleTagInFilter}
      />
      <Modal
        animation={false}
        show={modal.show}
        onHide={() => dispatch(hideModal())}
      >
        {ModalComponent ? <ModalComponent {...modal.props} /> : null}
      </Modal>
    </div>
  );
};

HuntViewMain.propTypes = {
  huntId: PropTypes.string.isRequired,
};
