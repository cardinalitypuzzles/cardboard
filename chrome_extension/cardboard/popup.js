// TODO: Default this to false and control this in the deployment process
const IS_PROD = false;

const PROD_URL = "https://cardboard.rocks";
const DEV_URL = "http://localhost:8000";

// TODO: Make this configurable
const HUNT_NUMBER = 1;

let TARGET_URL = DEV_URL;
if (IS_PROD) {
  TARGET_URL = PROD_URL;
}

// Read all puzzles and filter down to those that are metas.
const hunt_puzzles = await fetch(
  TARGET_URL + "/api/v1/hunts/" + HUNT_NUMBER + "/puzzles",
  {
    method: "GET",
  }
);
const response = await hunt_puzzles.json();

let metas = [];
let puzzles_by_url = new Map();
for (const puzzle of response) {
  if (puzzle.is_meta) {
    metas.push(puzzle.name);
  }
  if (puzzle.has_sheet) {
    puzzles_by_url.set(puzzle.url, puzzle.id);
  } else {
    puzzles_by_url.set(puzzle.url, -1);
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
      console.log(puzzles_by_url.get(tab.url));
      if (puzzles_by_url.get(tab.url) >= 0) {
        document.getElementById("puzzle_message").textContent = "Puzzle already exists:";
        document.getElementById("google_sheets_link").hidden = false;
        document.getElementById("google_sheets_link").href = TARGET_URL + "/puzzles/s/" + puzzles_by_url.get(tab.url);
      } else {
        document.getElementById("puzzle_message").textContent = "Puzzle already exists but the sheet is still being created.\nPlease wait 10 seconds then open the extension again.";
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

function pollForCreatedPuzzlePeriodically(target_url, interval, max_calls) {
  let call_count = 0;
  let interval_id = null;
  
  async function pollAndCheck() {
    call_count++;
    console.log(call_count);
    const hunt_puzzles = await fetch(
      TARGET_URL + "/api/v1/hunts/" + HUNT_NUMBER + "/puzzles",
      {
        method: "GET",
      }
    );
    const response = await hunt_puzzles.json();
    for (const puzzle of response) {
      if (puzzle.url === target_url & puzzle.has_sheet) {
        clearInterval(interval_id);
        console.log(puzzle.url);
        document.getElementById("google_sheets_link").hidden = false;
        document.getElementById("puzzle_message").textContent = "Puzzle created:";
        document.getElementById("google_sheets_link").href = TARGET_URL + "/puzzles/s/" + puzzle.id;
        console.log("Found puzzle");
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
    url: TARGET_URL,
    name: "csrftoken",
  });

  if (cardboard_cookie) {
    // Create puzzle. Puzzle name is limited to 80 characters
    fetch(TARGET_URL + "/api/v1/hunts/" + HUNT_NUMBER + "/puzzles", {
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
    document.getElementById("puzzle_message").textContent = "Puzzle created, waiting for Google Sheet to be created...";
    pollForCreatedPuzzlePeriodically(document.getElementById("puzzle_url").value, 2000, 15);
  } else {
    console.log("No cookie found");
  }
});