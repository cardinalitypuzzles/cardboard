chrome.runtime.onInstalled.addListener(() => {
  chrome.action.setBadgeText({
    text: 'ON'
  });
  console.log('on install');
});