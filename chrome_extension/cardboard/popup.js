const tabs = await chrome.tabs.query({
  active: true,
  currentWindow: true,
});
const collator = new Intl.Collator();
tabs.sort((a, b) => collator.compare(a.title, b.title));

const template = document.getElementById("li_template");
const elements = new Set();
let tab_name = '';
let tab_url = '';
for (const tab of tabs) {
  console.log(tab);
  const element = template.content.firstElementChild.cloneNode(true);
  console.log(element);
  
  if (tab.title != undefined) {
    console.log(tab.title);
    element.querySelector(".title").textContent = 'Puzzle: ' + tab.title;
    tab_name = tab.title;
  }
  if (tab.url != undefined) {
    console.log(tab.url);
    element.querySelector(".pathname").textContent = tab.url;
    tab_url = tab.url;
  }
  element.querySelector("a").addEventListener("click", async () => {
    // need to focus window as well as the active tab
    await chrome.tabs.update(tab.id, { active: true });
    await chrome.windows.update(tab.windowId, { focused: true });
  });

  elements.add(element);
}
document.querySelector("ul").append(...elements);
const button = document.querySelector("button");
button.addEventListener("click", async e => {
  e.preventDefault();
  const tabIds = tabs.map(({ id }) => id);
  const group = await chrome.tabs.group({ tabIds });
  await chrome.tabGroups.update(group, { title: "DOCS" });
  // Add API call here
  // https://dev.to/debosthefirst/how-to-build-a-chrome-extension-that-makes-api-calls-1g04
  fetch("http://localhost:8000/api/v1/hunts/3/puzzles", {
    method: "POST",
    mode: "cors",
    body: JSON.stringify({
      create_channels: false,
      is_meta: false,
      name: "B" + tab_name.slice(0, 30),
      url: tab_url
    }),
    headers: {
      "X-CSRFToken": "MxM3QPBhIakoOyIEiJq81ehOJMrrU7lC",
      "Content-Type": "application/json",
      "Cookie": "claimer=Max; sessionid=b7davlvw69lm7uqv742coj3m4iuoan0k; csrftoken=MxM3QPBhIakoOyIEiJq81ehOJMrrU7lC",
    },
  });
});