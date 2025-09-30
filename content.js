// Runs on LeetCode pages
console.log("LeetCode Committer content script loaded!");

// Extract code editor content from Monaco editor
function captureSolution() {
  // Query for the Monaco editor lines
  const lineNodes = document.querySelectorAll('.view-lines .view-line');

  if (!lineNodes || lineNodes.length === 0) {
    console.warn("No Monaco lines found");
    return null;
  }

  // Get text content directly from each line (avoids nested span duplication)
  const lines = Array.from(lineNodes).map(line => line.textContent);

  // Join with newlines to reconstruct the code
  return lines.join("\n");
}

// Example: Listen for popup.js request
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_SOLUTION") {
    sendResponse({ code: captureSolution() });
  }
});

