import Cookies from "js-cookie";

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
  const puzzlesApiUrl = `/api/v1/hunt/${huntId}/puzzles`;
  return fetch(puzzlesApiUrl).then(handleErrors);
}

function addPuzzle(huntId, data) {
  const puzzlesApiUrl = `/api/v1/hunt/${huntId}/puzzles`;
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
  const puzzleApiUrl = `/api/v1/hunt/${huntId}/puzzles/${puzzleId}`;
  return fetch(puzzleApiUrl, {
    method: "DELETE",
    headers: { "X-CSRFToken": Cookies.get("csrftoken") },
  }).then(handleErrors);
}

function updatePuzzle(huntId, puzzleId, data) {
  const puzzleApiUrl = `/api/v1/hunt/${huntId}/puzzles/${puzzleId}`;
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
  const answerApiUrl = `/api/v1/hunt/${huntId}/puzzles/${puzzleId}/answer`;
  return fetch(answerApiUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": Cookies.get("csrftoken"),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(handleErrors);
}

function getHunt(huntId) {
  const huntApiUrl = `/api/v1/hunt/${huntId}`;
  return fetch(huntApiUrl).then(handleErrors);
}

export default {
  getHunt,
  getPuzzles,
  addPuzzle,
  deletePuzzle,
  updatePuzzle,
  addAnswer,
};
