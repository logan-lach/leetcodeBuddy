// Runs on LeetCode pages
console.log("LeetCode Committer content script loaded!");

// Import constants (loaded via manifest.json)

// Inject Monaco accessor script into page context
(function injectMonacoAccessor() {
  console.log('[Content Script] Injecting Monaco accessor script');
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('js/monaco-accessor.js');
  script.onload = function() {
    console.log('[Content Script] Monaco accessor script loaded');
    this.remove();
  };
  script.onerror = function() {
    console.error('[Content Script] Failed to load Monaco accessor script');
  };
  (document.head || document.documentElement).appendChild(script);
})();

// Track if we've already processed an acceptance
let hasProcessedAcceptance = false;

// Show modal overlay with acceptance message
function showAcceptanceModal(code, metadata) {
  // Check if modal already exists
  if (document.getElementById('leetcode-committer-modal')) {
    return;
  }

  // Create modal overlay
  const modalOverlay = document.createElement('div');
  modalOverlay.id = 'leetcode-committer-modal';

  // Create modal content
  const modalContent = document.createElement('div');
  modalContent.id = 'leetcode-committer-modal-content';

  // Build modal HTML
  let modalHTML = `
    <div id="leetcode-committer-modal-header">
      <h2 id="leetcode-committer-modal-title">🎉 Solution Accepted!</h2>
      <button id="leetcode-committer-close">×</button>
    </div>
    <p id="leetcode-committer-message">
      Congratulations on the solve! Would you like to commit this to GitHub?
    </p>
  `;

  // Add metadata
  if (metadata && (metadata.title || metadata.problemSlug || metadata.difficulty)) {
    modalHTML += '<div id="leetcode-committer-metadata">';
    if (metadata.title) {
      modalHTML += `<p><strong>Problem:</strong> ${metadata.title}</p>`;
    }
    if (metadata.problemSlug) {
      modalHTML += `<p><strong>Slug:</strong> ${metadata.problemSlug}</p>`;
    }
    if (metadata.difficulty) {
      modalHTML += `<p><strong>Difficulty:</strong> ${metadata.difficulty}</p>`;
    }
    modalHTML += '</div>';
  }

  // Add code display
  modalHTML += `
    <div id="leetcode-committer-code-section">
      <span id="leetcode-committer-code-label">Your Solution:</span>
      <pre id="leetcode-committer-code">${code}</pre>
    </div>
  `;

  modalContent.innerHTML = modalHTML;
  modalOverlay.appendChild(modalContent);
  document.body.appendChild(modalOverlay);

  // Add close button functionality (after DOM insertion)
  const closeButton = document.getElementById('leetcode-committer-close');
  if (closeButton) {
    closeButton.addEventListener('click', (e) => {
      e.stopPropagation();
      modalOverlay.remove();
    });
  }

  // Click outside to close
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.remove();
    }
  });
}

// Extract code editor content from Monaco editor
function captureSolution() {
  return new Promise((resolve) => {
    console.log('[Content Script] captureSolution() called');

    // Try to get code from Monaco API first
    const timeout = setTimeout(() => {
      console.warn("[Content Script] Monaco API timeout, falling back to DOM scraping");
      resolve(captureSolutionFallback());
    }, 1000);

    // Set up response listener
    const responseHandler = (event) => {
      console.log('[Content Script] Received Monaco code response');
      clearTimeout(timeout);
      window.removeEventListener(CUSTOM_EVENTS.MONACO_CODE_RESPONSE, responseHandler);

      const code = event.detail?.code;
      if (code) {
        console.log("[Content Script] ✓ Code retrieved from Monaco API, length:", code.length);
        resolve(code);
      } else {
        console.warn("[Content Script] Monaco API returned null, falling back to DOM scraping");
        resolve(captureSolutionFallback());
      }
    };

    window.addEventListener(CUSTOM_EVENTS.MONACO_CODE_RESPONSE, responseHandler);

    // Request code from Monaco accessor
    console.log('[Content Script] Dispatching GET_MONACO_CODE event');
    window.dispatchEvent(new CustomEvent(CUSTOM_EVENTS.GET_MONACO_CODE));
  });
}

// Fallback method: Extract code from DOM
function captureSolutionFallback() {
  console.log('[Content Script] Using fallback DOM scraping method');

  // Query for the Monaco editor lines
  const lineNodes = document.querySelectorAll(LEETCODE_SELECTORS.MONACO_LINES);

  if (!lineNodes || lineNodes.length === 0) {
    console.warn("[Content Script] No Monaco lines found in DOM");
    return null;
  }

  console.log('[Content Script] Found', lineNodes.length, 'line nodes in DOM');

  // Get text content directly from each line (avoids nested span duplication)
  const lines = Array.from(lineNodes).map(line => line.textContent);

  // Join with newlines to reconstruct the code
  const code = lines.join("\n");
  console.log('[Content Script] DOM scraping complete, code length:', code.length);
  return code;
}

// Extract problem metadata
function extractMetadata() {
  // Problem title
  const titleElement = document.querySelector(LEETCODE_SELECTORS.TITLE_LINK) ||
                       document.querySelector(LEETCODE_SELECTORS.TITLE_DATA_ATTR);
  const title = titleElement?.textContent?.trim() || null;

  // Problem slug from URL - TODO: fix manually to extract problem number instead
  const urlMatch = window.location.pathname.match(LEETCODE_SELECTORS.PROBLEM_URL_PATTERN);
  const problemSlug = urlMatch ? urlMatch[1] : null;

  // Difficulty - look for badge with text-difficulty-{difficulty} class
  const difficultyElement = document.querySelector(LEETCODE_SELECTORS.DIFFICULTY_BADGE);
  let difficulty = null;
  if (difficultyElement) {
    const classList = Array.from(difficultyElement.classList);
    const difficultyClass = classList.find(c => c.startsWith(LEETCODE_SELECTORS.DIFFICULTY_CLASS_PREFIX));
    if (difficultyClass) {
      difficulty = difficultyClass.replace(LEETCODE_SELECTORS.DIFFICULTY_CLASS_PREFIX, '');
    }
  }

  return {
    title,
    problemSlug,
    difficulty
  };
}

// Detect successful submission
async function checkForAcceptedSubmission() {
  // Skip if we've already processed an acceptance
  if (hasProcessedAcceptance) {
    return;
  }

  const submissionResult = document.querySelector(LEETCODE_SELECTORS.SUBMISSION_RESULT);

  if (submissionResult && submissionResult.textContent.includes(LEETCODE_SELECTORS.ACCEPTED_TEXT)) {
    console.log("Accepted submission detected!");

    // Mark as processed to prevent duplicate triggers
    hasProcessedAcceptance = true;

    // Capture the code (now returns a Promise)
    const code = await captureSolution();

    if (code) {
      // Extract metadata
      const metadata = extractMetadata();

      // Store the submission data
      chrome.storage.local.set({
        [STORAGE_KEYS.LAST_ACCEPTED_SUBMISSION]: {
          code: code,
          metadata: metadata,
          timestamp: Date.now()
        }
      }, () => {
        console.log("Submission stored!", metadata);

        // Show modal overlay on the page
        showAcceptanceModal(code, metadata);
      });
    }
  }
}

// Set up MutationObserver to watch for submission results
const observer = new MutationObserver((mutations) => {
  // Only check when new nodes are added (not on initial page load)
  for (const mutation of mutations) {
    if (mutation.addedNodes.length > 0) {
      // Check if any added node contains the submission result
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          const submissionResult = node.querySelector?.(LEETCODE_SELECTORS.SUBMISSION_RESULT) ||
                                   (node.matches?.(LEETCODE_SELECTORS.SUBMISSION_RESULT) ? node : null);
          if (submissionResult) {
            checkForAcceptedSubmission();
            return;
          }
        }
      }
    }
  }
});

// Start observing the document for changes
observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Reset flag when URL changes (user navigates to new problem)
let lastUrl = location.href;
new MutationObserver(() => {
  const currentUrl = location.href;
  if (currentUrl !== lastUrl) {
    lastUrl = currentUrl;
    hasProcessedAcceptance = false;
    console.log("URL changed, reset acceptance flag");
  }
}).observe(document, { subtree: true, childList: true });

// Example: Listen for popup.js request
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === MESSAGE_TYPES.GET_SOLUTION) {
    // captureSolution is now async, handle it properly
    captureSolution().then(code => {
      sendResponse({ code: code });
    });
    return true; // Keep the message channel open for async response
  }
});

