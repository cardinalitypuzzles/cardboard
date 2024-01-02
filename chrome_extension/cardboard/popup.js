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
  elements.add(element);
}
document.querySelector("ul").append(...elements);
const button = document.querySelector("button");
button.addEventListener("click", async e => {
  e.preventDefault();
  // Get Cardboard cookie
  const cardboard_cookie = await chrome.cookies.get({ url: 'http://localhost:8000', name: 'csrftoken' });
  
  if (cardboard_cookie) {
    // Create puzzle. Puzzle name is limited to 30 characters 
    fetch("http://localhost:8000/api/v1/hunts/3/puzzles", {
      method: "POST",
      mode: "cors",
      body: JSON.stringify({
        create_channels: document.getElementById('create_channels').checked,
        is_meta: document.getElementById('is_meta').checked,
        name: document.getElementById('puzzle_name').value.slice(0, 30),
        url: document.getElementById('puzzle_url').value
      }),
      headers: {
        "X-CSRFToken": cardboard_cookie.value,
        "Content-Type": "application/json",
      },
    });
  } else {
    console.log('No cookie found');
  }
});

// Doing a GET in order to get the metas that you can assign this new puzzles to.
/*
const hunt_puzzles = await fetch("http://localhost:8000/api/v1/hunts/3/puzzles", {
  method: "GET",
});
const response = await hunt_puzzles.json();
console.log(response);
for (const puzzle of response) {
  if (puzzle.is_meta) {
    console.log(puzzle.name);
  }
}
*/