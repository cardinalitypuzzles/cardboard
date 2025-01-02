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
const hunt_metadata = await fetch(base_url + "/api/v1/hunts/" + hunt_id, {
  method: "GET",
});
const hunt_metadata_json = await hunt_metadata.json();
document.getElementById("hunt_name_tooltip").title =
  "To change hunts, go to " + base_url + "/hunts/ and select a different hunt.";

if (hunt_metadata_json.name != undefined) {
  document.getElementById("hunt_name").textContent = hunt_metadata_json.name;
  document.getElementById("hunt_name").href = hunt_url;
} else {
  document.getElementById("hunt_name").textContent = "No hunt name found";
}

// Read all puzzles.
const hunt_puzzles = await fetch(
  base_url + "/api/v1/hunts/" + hunt_id + "/puzzles",
  {
    method: "GET",
  }
);
const response = await hunt_puzzles.json();
let metas = [];
let puzzles_by_url = new Map();
const NO_SHEET_SENTINEL = -1;

for (const puzzle of response) {
  // Populate metas list for meta assignment dropdown.
  if (puzzle.is_meta) {
    metas.push(puzzle.name);
  }

  // Populate URL to Id map for all puzzles with sheets.
  if (puzzle.has_sheet) {
    puzzles_by_url.set(puzzle.url, puzzle.id);
  } else {
    // Assign
    puzzles_by_url.set(puzzle.url, NO_SHEET_SENTINEL);
  }
}

// There should only be one tab because there is only one currentWindow
// and active tab.
const tabs = await chrome.tabs.query({
  active: true,
  currentWindow: true,
});
const template = document.getElementById("li_template");
const elements = new Set();
for (const tab of tabs) {
  const element = template.content.firstElementChild.cloneNode(true);

  if (tab.title != undefined) {
    element.querySelector(".puzzle_name").value = tab.title;
  }
  if (tab.url != undefined) {
    element.querySelector(".puzzle_url").value = tab.url;
    // If a puzzle has already been made using this URL
    if (puzzles_by_url.get(tab.url) != undefined) {
      // If the sheet has already been made, display a link to the sheet.
      if (puzzles_by_url.get(tab.url) != NO_SHEET_SENTINEL) {
        document.getElementById("puzzle_message").textContent =
          "Puzzle already exists:";
        document.getElementById("google_sheets_link").hidden = false;
        document.getElementById("google_sheets_link").href =
          base_url + "/puzzles/s/" + puzzles_by_url.get(tab.url);
      } else {
        document.getElementById("puzzle_message").textContent =
          "Puzzle already exists but the sheet is still being created.\nPlease wait 10 seconds then open the extension again.";
      }
    }
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
}
document.querySelector("ul").append(...elements);

function pollForCreatedPuzzlePeriodically(puzzle_url, interval, max_calls) {
  let call_count = 0;
  let interval_id = null;

  async function pollAndCheck() {
    call_count++;
    const hunt_puzzles = await fetch(
      base_url + "/api/v1/hunts/" + hunt_id + "/puzzles",
      {
        method: "GET",
      }
    );
    const response = await hunt_puzzles.json();
    for (const puzzle of response) {
      // If the puzzle has been created and has a sheet, change the extension text to include a
      // link to the sheet and stop polling the website.
      if ((puzzle.url === puzzle_url) & puzzle.has_sheet) {
        clearInterval(interval_id);
        document.getElementById("google_sheets_link").hidden = false;
        document.getElementById("puzzle_message").textContent =
          "Puzzle created:";
        document.getElementById("google_sheets_link").href =
          base_url + "/puzzles/s/" + puzzle.id;
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

const button = document.querySelector("button");
button.addEventListener("click", async (e) => {
  e.preventDefault();
  // Get Cardboard cookie
  const cardboard_cookie = await chrome.cookies.get({
    url: base_url,
    name: "csrftoken",
  });

  if (cardboard_cookie) {
    // Create puzzle. Puzzle name is limited to 80 characters
    fetch(base_url + "/api/v1/hunts/" + hunt_id + "/puzzles", {
      method: "POST",
      mode: "cors",
      body: JSON.stringify({
        create_channels: document.getElementById("create_channels").checked,
        is_meta: document.getElementById("is_meta").checked,
        name: document.getElementById("puzzle_name").value.slice(0, 80),
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
