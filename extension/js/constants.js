// LeetCode Buddy Extension Constants
// Centralizes all hardcoded LeetCode page selectors for easy maintenance

// ============================================================================
// LEETCODE PAGE SELECTORS
// ============================================================================

// Monaco Editor Selectors
const LEETCODE_SELECTORS = {
  // Code Editor
  MONACO_LINES: '.view-lines .view-line',

  // Submission Result
  SUBMISSION_RESULT: 'span[data-e2e-locator="submission-result"]',
  ACCEPTED_TEXT: 'Accepted',

  // Problem Metadata
  TITLE_LINK: 'a[href^="/problems/"]',
  TITLE_DATA_ATTR: '[data-cy="question-title"]',
  DIFFICULTY_BADGE: '[class*="text-difficulty-"]',
  DIFFICULTY_CLASS_PREFIX: 'text-difficulty-',

  // URL Patterns
  PROBLEM_URL_PATTERN: /\/problems\/([^\/]+)/
};

// ============================================================================
// CHROME STORAGE KEYS
// ============================================================================

const STORAGE_KEYS = {
  LAST_ACCEPTED_SUBMISSION: 'lastAcceptedSubmission'
};

// ============================================================================
// MESSAGE TYPES
// ============================================================================

const MESSAGE_TYPES = {
  GET_SOLUTION: 'GET_SOLUTION',
  CAPTURE_CODE: 'CAPTURE_CODE'
};

// ============================================================================
// CUSTOM EVENT TYPES (for Monaco accessor communication)
// ============================================================================

const CUSTOM_EVENTS = {
  GET_MONACO_CODE: 'LEETCODE_BUDDY_GET_MONACO_CODE',
  MONACO_CODE_RESPONSE: 'LEETCODE_BUDDY_MONACO_CODE_RESPONSE',
  MONACO_ACCESSOR_READY: 'LEETCODE_BUDDY_MONACO_ACCESSOR_READY'
};
