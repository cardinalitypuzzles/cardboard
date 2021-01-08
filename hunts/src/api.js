import Cookies from "js-cookie";

const API_PREFIX = "/api/v1";

function handleErrors(response) {
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
      (err) => {
        throw new Error("An unknown error occurred.");
      }
    );
  }
  return response.json();
}

function getPuzzles(huntId) {
  const puzzlesApiUrl =`${API_PREFIX}/hunts/${huntId}/puzzles`;
  return fetch(puzzlesApiUrl).then(handleErrors);
}

function addPuzzle(huntId, data) {
  const puzzlesApiUrl =`${API_PREFIX}/hunts/${huntId}/puzzles`;
  return fetch(puzzlesApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function deletePuzzle(huntId, puzzleId) {
  const puzzleApiUrl =`${API_PREFIX}/hunts/${huntId}/puzzles/${puzzleId}`;
  return fetch(puzzleApiUrl, {
    method: "DELETE",
    headers: { "X-CSRFToken": Cookies.get("csrftoken") },
  }).then(handleErrors);
}

function updatePuzzle(huntId, puzzleId, data) {
  const puzzleApiUrl =`${API_PREFIX}/hunts/${huntId}/puzzles/${puzzleId}`;
  return fetch(puzzleApiUrl, {
    method: "PATCH",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function addAnswer(huntId, puzzleId, data) {
  const answerApiUrl =`${API_PREFIX}/puzzles/${puzzleId}/answers`;
  console.log(data);
  return fetch(answerApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function deleteAnswer(huntId, puzzleId, answerId) {
  const answerApiUrl =`${API_PREFIX}/puzzles/${puzzleId}/answers/${answerId}`;
  return fetch(answerApiUrl, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken"),
    },
  }).then(handleErrors);
}

function editAnswer(huntId, puzzleId, answerId, data) {
  const answerApiUrl =`${API_PREFIX}/puzzles/${puzzleId}/answers/${answerId}`;
  return fetch(answerApiUrl, {
    method: "PATCH",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function getHunt(huntId) {
  const huntApiUrl =`${API_PREFIX}/hunts/${huntId}`;
  return fetch(huntApiUrl).then(handleErrors);
}

function deletePuzzleTag(huntId, puzzleId, tagId) {
  const tagApiUrl =`${API_PREFIX}/puzzles/${puzzleId}/tags/${tagId}`;
  return fetch(tagApiUrl, {
    method: "DELETE",
    headers: { "X-CSRFToken": Cookies.get("csrftoken") },
  }).then(handleErrors);
}

function addPuzzleTag(huntId, puzzleId, data) {
  const tagsApiUrl =`${API_PREFIX}/puzzles/${puzzleId}/tags`;
  return fetch(tagsApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken"),
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
  deletePuzzleTag,
  addPuzzleTag,
};
