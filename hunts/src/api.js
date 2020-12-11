import Cookies from "js-cookie";

function getPuzzles(huntId) {
  const puzzlesApiUrl = `/api/v1/hunt/${huntId}/puzzles`;
  return fetch(puzzlesApiUrl).then((response) => {
    if (response.status > 400) {
      // TODO: error handling
      console.error("Get puzzles API failure", response);
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
    if (response.status > 400) {
      // TODO: error handling
      console.error("Delete puzzle API failure", response);
    }
    return response.json();
  });
}

function getHunt(huntId) {
  const huntApiUrl = `/api/v1/hunt/${huntId}`;
  return fetch(huntApiUrl).then((response) => {
    if (response.status > 400) {
      //TODO: Some error handling should go here
      console.error("Get hunt API failure", response);
    }
    return response.json();
  });
}

export default { getHunt, getPuzzles, deletePuzzle };
