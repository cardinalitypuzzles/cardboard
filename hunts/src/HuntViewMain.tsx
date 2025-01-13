import React from "react";
import { Alert, Button, Modal } from "react-bootstrap";
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
import EditNotesModal from "./EditNotesModal";
import EditPuzzleModal from "./EditPuzzleModal";
import AddPuzzleModal from "./AddPuzzleModal";
import SubmitAnswerModal from "./SubmitAnswerModal";
import EditPuzzleTagsModal from "./EditPuzzleTagsModal";
import useInterval from "@use-it/interval";
import {
  toggleFilterTag,
  getTagFilter,
  getSolveStateFilter,
} from "./filterSlice";
import TagPill from "./TagPill";
import { SolvedStateFilter } from "./solveStateFilter";
import { SiteHeader } from "./SiteHeader";

import type { Dispatch, RootState } from "./store";
import type { HuntId, PuzzleTag } from "./types";

const MODAL_COMPONENTS: Record<string, any> = {
  DELETE_PUZZLE: DeletePuzzleModal,
  EDIT_PUZZLE: EditPuzzleModal,
  ADD_PUZZLE: AddPuzzleModal,
  SUBMIT_ANSWER: SubmitAnswerModal,
  DELETE_ANSWER: DeleteAnswerModal,
  EDIT_ANSWER: EditAnswerModal,
  EDIT_NOTES: EditNotesModal,
  EDIT_TAGS: EditPuzzleTagsModal,
};

export const HuntViewMain = (props: { huntId: HuntId }) => {
  const tableData = useSelector<RootState, any>(selectPuzzleTableData);
  const modal = useSelector<RootState, any>((state) => state.modal);
  const hunt = useSelector<RootState, any>((state) => state.hunt);
  const alert = useSelector<RootState, any>((state) => state.alert);
  const filterTags = useSelector<RootState, PuzzleTag[]>(getTagFilter);

  const filterSolved = useSelector(getSolveStateFilter);

  const dispatch = useDispatch<Dispatch>();

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
    <>
      <SiteHeader />
      <div
        style={{
          margin: "0px auto",
          maxWidth: "1600px",
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
                  key={name}
                  onClick={() => dispatch(toggleFilterTag({ name, color, id }))}
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
