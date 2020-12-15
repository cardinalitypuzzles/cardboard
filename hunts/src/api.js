import Cookies from "js-cookie";

function getPuzzles(huntId) {
  const puzzlesApiUrl = `/api/v1/hunt/${huntId}/puzzles`;
  return fetch(puzzlesApiUrl).then((response) => {
    if (response.status >= 400) {
      // TODO: error handling
      throw new Error("Get puzzles API failure");
    }
    return response.json();
  });
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
  }).then((response) => {
    if (response.status >= 400) {
      // TODO: error handling
      throw new Error("Add puzzle API failure");
    }
    return response.json();
  });
}

function deletePuzzle(huntId, puzzleId) {
  const puzzleApiUrl = `/api/v1/hunt/${huntId}/puzzles/${puzzleId}`;
  return fetch(puzzleApiUrl, {
    method: "DELETE",
    headers: { "X-CSRFToken": Cookies.get("csrftoken") },
  }).then((response) => {
    if (response.status >= 400) {
      // TODO: error handling
      throw new Error("Delete puzzle API failure");
    }
    return response.json();
  });
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
  }).then((response) => {
    if (response.status >= 400) {
      // TODO: error handling
      throw new Error("Update puzzle API failure");
    }
    return response.json();
  });
}

function getHunt(huntId) {
  const huntApiUrl = `/api/v1/hunt/${huntId}`;
  return fetch(huntApiUrl).then((response) => {
    if (response.status >= 400) {
      //TODO: Some error handling should go here
      throw new Error("Get hunt API failure");
    }
    return response.json();
  });
}

export default { getHunt, getPuzzles, addPuzzle, deletePuzzle, updatePuzzle };
