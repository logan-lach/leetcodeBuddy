// Import constants
importScripts('constants.js');

chrome.runtime.onInstalled.addListener(() => {
  console.log("LeetCode Committer Extension Installed!");
});

// Handle messages from content.js or popup.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === MESSAGE_TYPES.CAPTURE_CODE) {
    console.log("Code captured:", message.payload);
    // TODO: send this to your backend / GitHub API logic
  }
});

