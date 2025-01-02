chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {
  if (request.huntId != undefined) {
    chrome.storage.local.set({ huntId: request.huntId });
  }
  if (sender.origin != undefined) {
    chrome.storage.local.set({ origin: sender.origin });
  }
  if (sender.url != undefined) {
    chrome.storage.local.set({ huntUrl: sender.url });
  }     
  sendResponse({ success: true, message: 'HuntId has been received' });
});
