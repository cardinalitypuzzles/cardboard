import React from "react";
import { useDispatch } from "react-redux";
import { addAnswer, addPuzzleTag } from "./puzzlesSlice";
import { hideModal } from "./modalSlice";

import type { Dispatch } from "./store";
import type { PuzzleId } from "./types";
import { SafeButton, SafeForm, SafeModal } from "./types";

type ChangeEvent = React.ChangeEvent<HTMLInputElement>;

function SubmitAnswerModal({ puzzleId, puzzleName } : { puzzleId: PuzzleId, puzzleName: string }) {
  const [newAnswer, setNewAnswer] = React.useState("");
  const [backsolved, setBacksolved] = React.useState(false);

  const dispatch = useDispatch<Dispatch>();
  const onSubmit = (e: ChangeEvent) => {
    e.preventDefault();
    if (backsolved) {
      dispatch(
        addPuzzleTag({
          puzzleId,
          name: "Backsolved",
          color: "success",
        })
      );
    }
    dispatch(
      addAnswer({
        puzzleId,
        body: { text: newAnswer },
      })
    ).finally(() => {
      dispatch(hideModal());
    });
    return false;
  };
  return (
    <>
      <SafeModal.Header closeSafeButton>
        <SafeModal.Title>Submit Answer for {puzzleName} </SafeModal.Title>
      </SafeModal.Header>
      <SafeForm onSubmit={onSubmit}>
        <SafeModal.Body>
          <SafeForm.Control
            required
            placeholder="Enter Answer"
            value={newAnswer}
            autoFocus
            onChange={(e: ChangeEvent) => setNewAnswer(e.target.value)}
          />
          <SafeForm.Check
            type="checkbox"
            defaultChecked={false}
            label="backsolved"
            value={backsolved}
            onChange={(e: ChangeEvent) => {
              e.target.checked ? setBacksolved(true) : setBacksolved(false);
            }}
          />
        </SafeModal.Body>
        <SafeModal.Footer>
          <SafeButton variant="secondary" onClick={() => dispatch(hideModal())}>
            Cancel
          </SafeButton>
          <SafeButton variant="primary" type="submit">
            Submit
          </SafeButton>
        </SafeModal.Footer>
      </SafeForm>
    </>
  );
}

export default SubmitAnswerModal;
