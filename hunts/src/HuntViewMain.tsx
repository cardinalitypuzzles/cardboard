import React from "react";
import { Alert, Button, Modal } from "react-bootstrap";
import PropTypes from "prop-types";
import api from "./api";
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
import TagPill from "./TagPill";
import { SolvedStateFilter } from "./solveStateFilter";
import { SiteHeader } from "./SiteHeader";
import { puzzleComparator } from "./utils";

import { useStore, RootState } from "./store";
import type { HuntId, PuzzleId, Puzzle } from "./types";

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

export interface PuzzleTable extends Puzzle {
  subRows: Puzzle[];
}

const makePuzzleTableData = (ids: Puzzle[]) => {
  // We need to construct the meta/subtree relationships.
  // Each meta that contains a puzzle gets a reference to the same
  // puzzle object. Then we can offload any actual graph traversal
  // to the table library.

  // Make a deep copy of everything first
  const rowsCopy: PuzzleTable[] = ids.map((id) => ({
    ...id,
    subRows: [],
  }));
  const rowMap: { [id: PuzzleId]: Puzzle } = {};
  rowsCopy.forEach((row) => {
    rowMap[row.id] = row;
  });
  // First give every meta references to all its children
  rowsCopy.forEach((row) => {
    if (row.feeders.length > 0) {
      row.subRows = [];
      row.feeders.forEach((subRowId) => {
        // This check is needed to deal with inconsistent data:
        // if we just deleted a puzzle, it may still appear as a feeder for
        // another puzzle if we haven't done a full refresh of the data yet
        if (subRowId in rowMap) {
          row.subRows.push(rowMap[subRowId]);
        }
      });
    }
  });
  // Once all the meta-child relationships are there, we can sort
  // every list of puzzles: all the subRows lists, and the list of outer puzzles as well.
  rowsCopy.forEach((row) => {
    if (row.subRows) {
      row.subRows.sort(puzzleComparator);
    }
  });
  const outerRows = rowsCopy.filter((row) => row.metas.length == 0);
  outerRows.sort(puzzleComparator);
  return outerRows;
};

export const HuntViewMain = (props: { huntId: HuntId }) => {
  const modal = useStore((state) => state.modalSlice);
  const hunt = useStore((state) => state.huntSlice);
  const alert = useStore((state) => state.alertSlice);
  const { fetchAllPuzzles, puzzles } = useStore((state) => state.puzzlesSlice);
  const { tags: filterTags, toggleFilterTag } = useStore(
    (state) => state.filterSlice
  );
  const filterSolved = useStore((state) => state.filterSlice.solveStateFilter);
  const { hideAlert } = useStore((state) => state.alertSlice);

  const l = useStore((state) => state.puzzlesSlice.lastUpdate);

  useInterval(fetchAllPuzzles, 10 * 1000);

  const ModalComponent = MODAL_COMPONENTS[modal.type];
  React.useEffect(() => {
    api.getHunt(props.huntId).then((response) => {
      hunt.set(response);
      fetchAllPuzzles();
    });
  }, [props.huntId]);

  React.useEffect(() => {
    if (alert.show) {
      const timer = setTimeout(hideAlert, 8 * 1000);
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
          onClose={() => hideAlert()}
        >
          {alert.text}
        </Alert>
        <HuntViewHeader hunt={hunt.hunt} />
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
            {filterTags.map((tag) => {
              // This use of toggleFilterTag will remove the tag from the list
              return (
                <TagPill
                  name={tag.name}
                  color={tag.color}
                  key={tag.name}
                  onClick={() => toggleFilterTag(tag)}
                />
              );
            })}
          </div>

          <Button
            variant="primary"
            size="lg"
            onClick={() =>
              modal.showModal({
                type: "ADD_PUZZLE",
                props: {
                  huntId: props.huntId,
                },
              })
            }
          >
            Add Puzzle
          </Button>
        </div>
        <PuzzleTable
          data={makePuzzleTableData(Object.values(puzzles))}
          filterSolved={filterSolved}
          filterTags={filterTags}
        />
        <Modal
          animation={false}
          show={modal.show}
          onHide={modal.hideModal}
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
