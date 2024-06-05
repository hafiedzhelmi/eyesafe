chrome.runtime.onInstalled.addListener(function () {
  chrome.storage.local.set({ sensitivity: "5", filterEnabled: true });
  console.log(
    "Extension installed. Default sensitivity set to Level 5 and filter enabled."
  );
});
