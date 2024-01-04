import React from "react";
import PropTypes from "prop-types";
import { useSelector, useDispatch } from "react-redux";
import { fetchPuzzles, selectPuzzleTableData } from "./puzzlesSlice";
import { fetchHunt } from "./huntSlice";
import { showModal, hideModal } from "./modalSlice";
import { hideAlert } from "./alertSlice";
import { PuzzleTable } from "./puzzle-table";
import HuntViewHeader from "./HuntViewHeader";
import GlobalFilter from "./GlobalFilter";
import DeleteAnswerModal from "./DeleteAnswerModal";
import DeletePuzzleModal from "./DeletePuzzleModal";
import EditAnswerModal from "./EditAnswerModal";
import EditPuzzleModal from "./EditPuzzleModal";
import AddPuzzleModal from "./AddPuzzleModal";
import SubmitAnswerModal from "./SubmitAnswerModal";
import EditPuzzleTagsModal from "./EditPuzzleTagsModal";
import useInterval from "@use-it/interval";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import Alert from "react-bootstrap/Alert";
import {
  toggleFilterTag,
  getTagFilter,
  getSolveStateFilter,
} from "./filterSlice";
import TagPill from "./TagPill";
import { SolvedStateFilter } from "./solveStateFilter";
import { SiteHeader } from "./SiteHeader";

const MODAL_COMPONENTS = {
  DELETE_PUZZLE: DeletePuzzleModal,
  EDIT_PUZZLE: EditPuzzleModal,
  ADD_PUZZLE: AddPuzzleModal,
  SUBMIT_ANSWER: SubmitAnswerModal,
  DELETE_ANSWER: DeleteAnswerModal,
  EDIT_ANSWER: EditAnswerModal,
  EDIT_TAGS: EditPuzzleTagsModal,
};

export const HuntViewMain = (props) => {
  const tableData = useSelector(selectPuzzleTableData);
  const modal = useSelector((state) => state.modal);
  const hunt = useSelector((state) => state.hunt);
  const alert = useSelector((state) => state.alert);
  const filterTags = useSelector(getTagFilter);

  const filterSolved = useSelector(getSolveStateFilter);

  const dispatch = useDispatch();

  const updatePuzzleAndHuntData = () => {
    dispatch(fetchPuzzles(props.huntId));
    dispatch(fetchHunt(props.huntId));
  };

  useInterval(updatePuzzleAndHuntData, 10 * 1000);

  const ModalComponent = MODAL_COMPONENTS[modal.type];
  React.useEffect(() => {
    dispatch(fetchHunt(props.huntId));
    updatePuzzleAndHuntData();
  }, [props.huntId]);

  React.useEffect(() => {
    if (alert.show) {
      const timer = setTimeout(() => dispatch(hideAlert()), 8 * 1000);
      return () => clearTimeout(timer);
    }
  }, [alert.id]);

  return (
    <>
      <SiteHeader />
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
            <GlobalFilter />
            <SolvedStateFilter />
          </div>
          <div>
            {filterTags.length > 0 ? "Viewing puzzles with tags: " : ""}
            {filterTags.map(({ name, color, id }) => {
              // This use of toggleFilterTag will remove the tag from the list
              return (
                <TagPill
                  name={name}
                  color={color}
                  id={id}
                  puzzleId={null}
                  key={name}
                  onDelete={() =>
                    dispatch(toggleFilterTag({ name, color, id }))
                  }
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
          data={tableData}
          filterSolved={filterSolved}
          filterTags={filterTags}
        />
        <Modal
          animation={false}
          show={modal.show}
          onHide={() => dispatch(hideModal())}
          scrollable={true}
        >
          {ModalComponent ? <ModalComponent {...modal.props} /> : null}
        </Modal>
      </div>
    </>
  );
};

HuntViewMain.propTypes = {
  huntId: PropTypes.string.isRequired,
};
