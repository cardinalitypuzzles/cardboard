import Cookies from "js-cookie";

import { AnswerId, HuntId, PuzzleId, TagId } from "./types";

const API_PREFIX = "/api/v1";

function handleErrors(response: Response) {
  if (!response.ok) {
    return response.json().then(
      (json) => {
        if (json.detail) {
          throw new Error(json.detail);
        } else if (json.non_field_errors) {
          throw new Error(json.non_field_errors[0]);
        } else {
          throw new Error(JSON.stringify(json));
        }
      },
      () => {
        throw new Error("An unknown error occurred.");
      }
    );
  }
  return response.json();
}

function getPuzzles(huntId: HuntId) {
  const puzzlesApiUrl = `${API_PREFIX}/hunts/${huntId}/puzzles`;
  return fetch(puzzlesApiUrl).then(handleErrors);
}

function addPuzzle(
  huntId: HuntId,
  data: {
    name: string;
    url: string;
    is_meta: boolean;
    create_channels: boolean;
    assigned_meta: string;
  }
) {
  const puzzlesApiUrl = `${API_PREFIX}/hunts/${huntId}/puzzles`;
  return fetch(puzzlesApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken")!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function deletePuzzle(huntId: HuntId, puzzleId: PuzzleId) {
  const puzzleApiUrl = `${API_PREFIX}/hunts/${huntId}/puzzles/${puzzleId}`;
  return fetch(puzzleApiUrl, {
    method: "DELETE",
    headers: { "X-CSRFToken": Cookies.get("csrftoken")! },
  }).then(handleErrors);
}

function updatePuzzle(
  huntId: HuntId,
  puzzleId: PuzzleId,
  data: {
    name?: string;
    url?: string;
    is_meta?: boolean;
    create_channels?: boolean;
    status?: string;
  }
) {
  const puzzleApiUrl = `${API_PREFIX}/hunts/${huntId}/puzzles/${puzzleId}`;
  return fetch(puzzleApiUrl, {
    method: "PATCH",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken")!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function addAnswer(puzzleId: PuzzleId, data: { text: string }) {
  const answerApiUrl = `${API_PREFIX}/puzzles/${puzzleId}/answers`;
  return fetch(answerApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken")!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function deleteAnswer(puzzleId: PuzzleId, answerId: AnswerId) {
  const answerApiUrl = `${API_PREFIX}/puzzles/${puzzleId}/answers/${answerId}`;
  return fetch(answerApiUrl, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken")!,
    },
  }).then(handleErrors);
}

function editAnswer(
  puzzleId: PuzzleId,
  answerId: AnswerId,
  data: { text: string }
) {
  const answerApiUrl = `${API_PREFIX}/puzzles/${puzzleId}/answers/${answerId}`;
  return fetch(answerApiUrl, {
    method: "PATCH",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken")!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function editNotes(puzzleId: PuzzleId, data: { text: string }) {
  const notesApiUrl = `${API_PREFIX}/puzzles/${puzzleId}/notes`;
  return fetch(notesApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken")!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function getHunt(huntId: HuntId) {
  const huntApiUrl = `${API_PREFIX}/hunts/${huntId}`;
  return fetch(huntApiUrl).then(handleErrors);
}

function deletePuzzleTag(puzzleId: PuzzleId, tagId: TagId) {
  const tagApiUrl = `${API_PREFIX}/puzzles/${puzzleId}/tags/${tagId}`;
  return fetch(tagApiUrl, {
    method: "DELETE",
    headers: { "X-CSRFToken": Cookies.get("csrftoken")! },
  }).then(handleErrors);
}

function addPuzzleTag(
  puzzleId: PuzzleId,
  data: { name: string; color: string }
) {
  const tagsApiUrl = `${API_PREFIX}/puzzles/${puzzleId}/tags`;
  return fetch(tagsApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken")!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

export default {
  getHunt,
  getPuzzles,
  addPuzzle,
  deletePuzzle,
  updatePuzzle,
  addAnswer,
  deleteAnswer,
  editAnswer,
  editNotes,
  deletePuzzleTag,
  addPuzzleTag,
};
