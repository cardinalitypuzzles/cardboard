// Get hunt information from local Chrome storage
async function getHuntData() {
  const data = await chrome.storage.local.get();
  return data;
}

const hunt_data = await getHuntData();
const hunt_id = hunt_data["huntId"];
const hunt_url = hunt_data["huntUrl"];
const base_url = hunt_data["origin"];

// Exit script if hunt information isn't found.
if (hunt_id === undefined) {
  throw new Error("No hunt_id found");
}
if (hunt_url === undefined) {
  throw new Error("No hunt_url found");
}
if (base_url === undefined) {
  throw new Error("No base_url found");
}

// Get hunt name from site.
const hunt_metadata = await fetch(`${base_url}/api/v1/hunts/${hunt_id}`, {
  method: "GET",
});
const hunt_metadata_json = await hunt_metadata.json();
document.getElementById(
  "hunt_name_tooltip"
).title = `To change hunts, go to ${base_url}/hunts/ and select a different hunt.`;

if (hunt_metadata_json.name != undefined) {
  document.getElementById("hunt_name").textContent = hunt_metadata_json.name;
  document.getElementById("hunt_name").href = hunt_url;
} else {
  document.getElementById("hunt_name").textContent = "No hunt name found";
}

// Read all puzzles.
const hunt_puzzles = await fetch(
  `${base_url}/api/v1/hunts/${hunt_id}/puzzles`,
  {
    method: "GET",
  }
);
const response = await hunt_puzzles.json();
let metas = [];
let puzzles_by_url = new Map();

for (const puzzle of response) {
  // Populate metas list for meta assignment dropdown.
  if (puzzle.is_meta) {
    metas.push(puzzle.name);
  }

  puzzles_by_url.set(puzzle.url, puzzle);
}

const setTextInputValue = (el, str) => {
  const maxlength = +el.getAttribute("maxlength");
  el.value = str.substring(0, maxlength);
};

function getPuzzleFromGoogleSheet(puzzles_by_url, tab_url, tab_title) {
  for (let [puzzle_url, puzzle] of puzzles_by_url) {
    const puzzle_title = puzzle.name;
    if (
      tab_title.endsWith(puzzle_title + " - Google Sheets") &&
      tab_url.includes("docs.google.com/spreadsheets")
    ) {
      return puzzle;
    }
  }
  return undefined;
}

// There should only be one tab because there is only one currentWindow
// and active tab.
const tabs = await chrome.tabs.query({
  active: true,
  currentWindow: true,
});
const elements = new Set();
for (const tab of tabs) {
  if (tab.url !== undefined) {
    const puzzle_from_sheet = getPuzzleFromGoogleSheet(
      puzzles_by_url,
      tab.url,
      tab.title
    );
    // If a puzzle has already been made using this URL
    if (puzzles_by_url.get(tab.url) !== undefined) {
      const puzzle = puzzles_by_url.get(tab.url);
      const template = document.getElementById("existing_puzzle_template");
      const element = template.content.firstElementChild.cloneNode(true);

      // If the sheet has already been made, display a link to the sheet.
      if (puzzle.has_sheet) {
        document.getElementById("puzzle_message").textContent =
          "Puzzle already exists:";
        document.getElementById("google_sheets_link").hidden = false;
        document.getElementById(
          "google_sheets_link"
        ).href = `${base_url}/puzzles/s/${puzzle.id}`;
      } else {
        document.getElementById("puzzle_message").textContent =
          "Puzzle already exists but the sheet is still being created.\nPlease wait 10 seconds then open the extension again.";
      }

      let puzzle_status_dropdown = element.querySelector(".puzzle_status");
      // Only show the SOLVED status if the puzzle is currently SOLVED.
      if (puzzle.status === "SOLVED") {
        let option = document.createElement("option");
        option.text = "SOLVED";
        option.value = "SOLVED";
        option.key = "SOLVED";
        puzzle_status_dropdown.add(option);
      }
      puzzle_status_dropdown.value = puzzle.status;

      // Add metas to dropdown
      let meta_dropdown = element.querySelector(".puzzle_meta");
      for (const meta of metas) {
        let option = document.createElement("option");
        option.text = meta;
        option.value = meta;
        option.key = meta;
        meta_dropdown.add(option);
      }

      // If a puzzle belongs to multiple metas, just show one of them.
      let backsolved_tag_id = undefined;
      for (const tag of puzzle.tags) {
        if (tag.is_meta && tag.name !== puzzle.name) {
          meta_dropdown.value = tag.name;
        }
        if (tag.name === "Backsolved") {
          element.querySelector("#is_backsolved").checked = true;
          backsolved_tag_id = tag.id;
        }
      }

      const existing_answers = new Set();
      for (const guess of puzzle.guesses) {
        if (guess.text != undefined) {
          element.querySelector(".puzzle_answer").value = guess.text;
          existing_answers.add(guess.text);
        }
      }
      if (puzzle.notes !== undefined) {
        element.querySelector(".puzzle_notes").value = puzzle.notes;
      }
      elements.add(element);

      const button = document.getElementById("puzzle_button");
      button.textContent = "Edit Puzzle";
      button.addEventListener("click", async (e) => {
        e.preventDefault();
        // Get Cardboard cookie
        const cardboard_cookie = await chrome.cookies.get({
          url: base_url,
          name: "csrftoken",
        });

        if (cardboard_cookie) {
          // Change status if different
          if (
            puzzle.status !== document.getElementById("puzzle_status").value
          ) {
            fetch(`${base_url}/api/v1/hunts/${hunt_id}/puzzles/${puzzle.id}`, {
              method: "PATCH",
              mode: "cors",
              body: JSON.stringify({
                status: document.getElementById("puzzle_status").value,
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          }

          // If a new meta is selected, send request to assign meta.
          let is_new_meta = true;
          for (const tag of puzzle.tags) {
            if (tag.name === document.getElementById("puzzle_meta").value) {
              is_new_meta = false;
              break;
            }
          }
          if (
            is_new_meta &&
            document.getElementById("puzzle_meta").value !== "None"
          ) {
            fetch(`${base_url}/api/v1/puzzles/${puzzle.id}/tags`, {
              method: "POST",
              mode: "cors",
              body: JSON.stringify({
                name: document.getElementById("puzzle_meta").value,
                color: "dark",
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          }

          // If the note is changed, send request to update note.
          if (document.getElementById("puzzle_notes").value !== puzzle.notes) {
            fetch(`${base_url}/api/v1/puzzles/${puzzle.id}/notes`, {
              method: "POST",
              mode: "cors",
              body: JSON.stringify({
                text: document.getElementById("puzzle_notes").value,
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          }

          const answer = document.getElementById("puzzle_answer").value;
          // Submit answer
          if (answer != "" && !existing_answers.has(answer)) {
            fetch(`${base_url}/api/v1/puzzles/${puzzle.id}/answers`, {
              method: "POST",
              mode: "cors",
              body: JSON.stringify({
                text: answer,
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          }
          // Toggle backsolved-ness
          if (
            document.getElementById("is_backsolved").checked &&
            backsolved_tag_id === undefined
          ) {
            fetch(`${base_url}/api/v1/puzzles/${puzzle.id}/tags`, {
              method: "POST",
              mode: "cors",
              body: JSON.stringify({
                name: "Backsolved",
                color: "success",
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          } else if (
            !document.getElementById("is_backsolved").checked &&
            backsolved_tag_id !== undefined
          ) {
            fetch(
              `${base_url}/api/v1/puzzles/${puzzle.id}/tags/${backsolved_tag_id}`,
              {
                method: "DELETE",
                mode: "cors",
                headers: {
                  "X-CSRFToken": cardboard_cookie.value,
                  "Content-Type": "application/json",
                },
              }
            );
          }
        } else {
          console.log("No cookie found");
        }
      });
    } else if (puzzle_from_sheet !== undefined) {
      // If you are on the sheets tab for a puzzle.
      const template = document.getElementById("existing_puzzle_template");
      const element = template.content.firstElementChild.cloneNode(true);

      document.getElementById("puzzle_message").textContent =
        "Puzzle already exists:";
      document.getElementById("puzzle_link").hidden = false;
      document.getElementById("puzzle_link").href = puzzle_from_sheet.url;

      let puzzle_status_dropdown = element.querySelector(".puzzle_status");
      // Only show the SOLVED status if the puzzle is currently SOLVED.
      if (puzzle_from_sheet.status === "SOLVED") {
        let option = document.createElement("option");
        option.text = "SOLVED";
        option.value = "SOLVED";
        option.key = "SOLVED";
        puzzle_status_dropdown.add(option);
      }
      puzzle_status_dropdown.value = puzzle_from_sheet.status;

      // Add metas to dropdown
      let meta_dropdown = element.querySelector(".puzzle_meta");
      for (const meta of metas) {
        let option = document.createElement("option");
        option.text = meta;
        option.value = meta;
        option.key = meta;
        meta_dropdown.add(option);
      }

      // If a puzzle belongs to multiple metas, just show one of them.
      let backsolved_tag_id = undefined;
      for (const tag of puzzle_from_sheet.tags) {
        if (tag.is_meta && tag.name !== puzzle_from_sheet.name) {
          meta_dropdown.value = tag.name;
        }
        if (tag.name === "Backsolved") {
          element.querySelector("#is_backsolved").checked = true;
          backsolved_tag_id = tag.id;
        }
      }

      const existing_answers = new Set();
      for (const guess of puzzle_from_sheet.guesses) {
        if (guess.text != undefined) {
          element.querySelector(".puzzle_answer").value = guess.text;
          existing_answers.add(guess.text);
        }
      }
      if (puzzle_from_sheet.notes !== undefined) {
        element.querySelector(".puzzle_notes").value = puzzle_from_sheet.notes;
      }
      elements.add(element);

      const button = document.getElementById("puzzle_button");
      button.textContent = "Edit Puzzle";
      button.addEventListener("click", async (e) => {
        e.preventDefault();
        // Get Cardboard cookie
        const cardboard_cookie = await chrome.cookies.get({
          url: base_url,
          name: "csrftoken",
        });

        if (cardboard_cookie) {
          // Change status if different
          if (
            puzzle_from_sheet.status !==
            document.getElementById("puzzle_status").value
          ) {
            fetch(
              `${base_url}/api/v1/hunts/${hunt_id}/puzzles/${puzzle_from_sheet.id}`,
              {
                method: "PATCH",
                mode: "cors",
                body: JSON.stringify({
                  status: document.getElementById("puzzle_status").value,
                }),
                headers: {
                  "X-CSRFToken": cardboard_cookie.value,
                  "Content-Type": "application/json",
                },
              }
            );
          }

          // If meta is selected, send request to assign meta.
          let is_new_meta = true;
          for (const tag of puzzle_from_sheet.tags) {
            if (tag.name === document.getElementById("puzzle_meta").value) {
              is_new_meta = false;
              break;
            }
          }
          if (
            is_new_meta &&
            document.getElementById("puzzle_meta").value !== "None"
          ) {
            fetch(`${base_url}/api/v1/puzzles/${puzzle_from_sheet.id}/tags`, {
              method: "POST",
              mode: "cors",
              body: JSON.stringify({
                name: document.getElementById("puzzle_meta").value,
                color: "dark",
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          }

          // If the note is changed, send request to update note.
          if (
            document.getElementById("puzzle_notes").value !==
            puzzle_from_sheet.notes
          ) {
            fetch(`${base_url}/api/v1/puzzles/${puzzle_from_sheet.id}/notes`, {
              method: "POST",
              mode: "cors",
              body: JSON.stringify({
                text: document.getElementById("puzzle_notes").value,
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          }
          const answer = document.getElementById("puzzle_answer").value;
          // Submit answer
          if (answer != "" && !existing_answers.has(answer)) {
            fetch(
              `${base_url}/api/v1/puzzles/${puzzle_from_sheet.id}/answers`,
              {
                method: "POST",
                mode: "cors",
                body: JSON.stringify({
                  text: answer,
                }),
                headers: {
                  "X-CSRFToken": cardboard_cookie.value,
                  "Content-Type": "application/json",
                },
              }
            );
          }
          // Toggle backsolved-ness
          if (
            document.getElementById("is_backsolved").checked &&
            backsolved_tag_id === undefined
          ) {
            fetch(`${base_url}/api/v1/puzzles/${puzzle_from_sheet.id}/tags`, {
              method: "POST",
              mode: "cors",
              body: JSON.stringify({
                name: "Backsolved",
                color: "success",
              }),
              headers: {
                "X-CSRFToken": cardboard_cookie.value,
                "Content-Type": "application/json",
              },
            });
          } else if (
            !document.getElementById("is_backsolved").checked &&
            backsolved_tag_id !== undefined
          ) {
            fetch(
              `${base_url}/api/v1/puzzles/${puzzle_from_sheet.id}/tags/${backsolved_tag_id}`,
              {
                method: "DELETE",
                mode: "cors",
                headers: {
                  "X-CSRFToken": cardboard_cookie.value,
                  "Content-Type": "application/json",
                },
              }
            );
          }
        } else {
          console.log("No cookie found");
        }
      });
    } else {
      // If a puzzle doesn't yet exist for this URL.
      const template = document.getElementById("new_puzzle_template");
      const element = template.content.firstElementChild.cloneNode(true);
      element.querySelector(".puzzle_url").value = tab.url;
      if (tab.title != undefined) {
        setTextInputValue(element.querySelector(".puzzle_name"), tab.title);
      }
      // Add metas to dropdown
      let meta_dropdown = element.querySelector(".puzzle_meta");
      for (const meta of metas) {
        let option = document.createElement("option");
        option.text = meta;
        option.value = meta;
        option.key = meta;
        meta_dropdown.add(option);
      }
      elements.add(element);

      const button = document.getElementById("puzzle_button");
      button.textContent = "Add Puzzle";
      button.addEventListener("click", async (e) => {
        e.preventDefault();
        // Get Cardboard cookie
        const cardboard_cookie = await chrome.cookies.get({
          url: base_url,
          name: "csrftoken",
        });

        if (cardboard_cookie) {
          // Create puzzle.
          fetch(`${base_url}/api/v1/hunts/${hunt_id}/puzzles`, {
            method: "POST",
            mode: "cors",
            body: JSON.stringify({
              create_channels:
                document.getElementById("create_channels").checked,
              is_meta: document.getElementById("is_meta").checked,
              name: document.getElementById("puzzle_name").value,
              url: document.getElementById("puzzle_url").value,
              assigned_meta: document.getElementById("puzzle_meta").value,
            }),
            headers: {
              "X-CSRFToken": cardboard_cookie.value,
              "Content-Type": "application/json",
            },
          });
          document.getElementById("puzzle_message").textContent =
            "Puzzle created, waiting for Google Sheet to be created...";

          // Poll website every 2 seconds for 30 seconds waiting for the sheet to be created.
          pollForCreatedPuzzlePeriodically(
            document.getElementById("puzzle_url").value,
            2000,
            15
          );
        } else {
          console.log("No cookie found");
        }
      });
    }
  }
}
document.querySelector("ul").append(...elements);

function pollForCreatedPuzzlePeriodically(puzzle_url, interval, max_calls) {
  let call_count = 0;
  let interval_id = null;

  async function pollAndCheck() {
    call_count++;
    const hunt_puzzles = await fetch(
      `${base_url}/api/v1/hunts/${hunt_id}/puzzles`,
      {
        method: "GET",
      }
    );
    const response = await hunt_puzzles.json();
    for (const puzzle of response) {
      // If the puzzle has been created and has a sheet, change the extension text to include a
      // link to the sheet and stop polling the website.
      if (puzzle.url === puzzle_url && puzzle.has_sheet) {
        clearInterval(interval_id);
        document.getElementById("google_sheets_link").hidden = false;
        document.getElementById("puzzle_message").textContent =
          "Puzzle created:";
        document.getElementById(
          "google_sheets_link"
        ).href = `${base_url}/puzzles/s/${puzzle.id}`;
      }
    }
    if (call_count >= max_calls) {
      clearInterval(interval_id);
      console.log("Max calls reached");
    }
  }

  pollAndCheck();
  interval_id = setInterval(pollAndCheck, interval);
}
