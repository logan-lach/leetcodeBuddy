chrome.runtime.onInstalled.addListener(() => {
  console.log("LeetCode Committer Extension Installed!");
});

// Later you can handle messages from content.js or popup.js here
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CAPTURE_CODE") {
    console.log("Code captured:", message.payload);
    // TODO: send this to your backend / GitHub API logic
  }
});

