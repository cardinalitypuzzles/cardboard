const IS_PROD = true;

const PROD_URL = "https://cardboard.rocks";
const DEV_URL = "http://localhost:8000";

// TODO: Make this configurable
const HUNT_NUMBER = 10;

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
for (const puzzle of response) {
  if (puzzle.is_meta) {
    metas.push(puzzle.name);
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

const button = document.querySelector("button");
button.addEventListener("click", async (e) => {
  e.preventDefault();
  // Get Cardboard cookie
  const cardboard_cookie = await chrome.cookies.get({
    url: TARGET_URL,
    name: "csrftoken",
  });

  if (cardboard_cookie) {
    // Create puzzle. Puzzle name is limited to 30 characters
    fetch(TARGET_URL + "/api/v1/hunts/" + HUNT_NUMBER + "/puzzles", {
      method: "POST",
      mode: "cors",
      body: JSON.stringify({
        create_channels: document.getElementById("create_channels").checked,
        is_meta: document.getElementById("is_meta").checked,
        name: document.getElementById("puzzle_name").value.slice(0, 30),
        url: document.getElementById("puzzle_url").value,
        assigned_meta: document.getElementById("puzzle_meta").value,
      }),
      headers: {
        "X-CSRFToken": cardboard_cookie.value,
        "Content-Type": "application/json",
      },
    });
  } else {
    console.log("No cookie found");
  }
});
