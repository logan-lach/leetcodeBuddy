// GitHub OAuth Configuration
// TODO: Replace with your GitHub OAuth App Client ID
const GITHUB_CLIENT_ID = 'Ov23li0B5ihAdLrIpijR';
const REDIRECT_URL = chrome.identity.getRedirectURL();

// Check authentication state on popup load
document.addEventListener('DOMContentLoaded', () => {
  console.log("Checking auth state");
  checkAuthState();
});

// Sign in with GitHub button handler
document.getElementById("githubSignIn").addEventListener("click", () => {
  console.log("Sign in with GitHub clicked");
  initiateGitHubOAuth();
});

/**
 * Validates if a GitHub token is still valid by making a test API call
 * TODO: Update this to work with the new backend auth flow
 */
async function validateGitHubToken(token) {
  try {
    const response = await fetch('https://api.github.com/user', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });

    // If we get 200, token is valid
    // If we get 401, token is invalid/revoked
    return response.ok;
  } catch (error) {
    console.error('Error validating GitHub token:', error);
    // On network error, assume token might still be valid
    // (don't force re-auth due to temporary network issues)
    return true;
  }
}

/**
 * Checks if user is authenticated and updates UI accordingly
 */
async function checkAuthState() {
  chrome.storage.local.get(['githubToken'], async (result) => {
    if (result.githubToken) {
      // Validate token with GitHub API
      const isValid = await validateGitHubToken(result.githubToken);

      if (isValid) {
        // Token is valid - show signed-in view
        console.log(`The current github token is valid! github token: ${result.githubToken}`)
        showSignedInView();
      } else {
        // Token is invalid/revoked - clear it and show sign-in view
        console.log('GitHub token is invalid or revoked, clearing...');
        chrome.storage.local.remove(['githubToken'], () => {
          showSignInView();
        });
      }
    } else {
      // User is not authenticated - show sign-in view
      console.log("User is currently not authenticated");
      showSignInView();
    }
  });
}

/**
 * Shows the signed-in view and hides the sign-in view
 */
function showSignedInView() {
  document.getElementById('signInView').style.display = 'none';
  document.getElementById('signedInView').style.display = 'block';
}

/**
 * Shows the sign-in view and hides the signed-in view
 */
function showSignInView() {
  document.getElementById('signInView').style.display = 'block';
  document.getElementById('signedInView').style.display = 'none';
}

/**
 * Initiates GitHub OAuth flow using chrome.identity.launchWebAuthFlow
 */
function initiateGitHubOAuth() {
  // Construct GitHub OAuth authorization URL
  const authUrl = new URL('https://github.com/login/oauth/authorize');
  authUrl.searchParams.set('client_id', GITHUB_CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', REDIRECT_URL);
  authUrl.searchParams.set('scope', 'repo'); // Request repo access for committing code

  console.log('Launching OAuth flow with redirect URL:', REDIRECT_URL);

  // Launch the OAuth flow in a new window
  chrome.identity.launchWebAuthFlow(
    {
      url: authUrl.toString(),
      interactive: true
    },
    async (redirectUrl) => {
      if (chrome.runtime.lastError) {
        console.error('OAuth Error:', chrome.runtime.lastError);
        alert('Failed to authenticate with GitHub: ' + chrome.runtime.lastError.message);
        return;
      }

      if (redirectUrl) {
        // Extract the authorization code from the redirect URL
        const code = extractTokenFromUrl(redirectUrl);

        if (code) {
          // Exchange the code for an access token via the backend
          const userData = await exchangeCodeForToken(code);

          if (userData) {
            // Store the user data in chrome.storage.local
            storeGitHubToken(userData);
          } else {
            console.error('Failed to exchange code for token');
            alert('Failed to retrieve access token from GitHub');
          }
        } else {
          console.error('No authorization code found in redirect URL');
          alert('Failed to retrieve authorization code from GitHub');
        }
      }
    }
  );
}

/**
 * Exchanges the authorization code for an access token via the backend
 */
async function exchangeCodeForToken(code) {
  try {
    const response = await fetch(`https://leetcode-buddy-backend.vercel.app/api/authorize?code=${code}`);

    if (!response.ok) {
      // TODO: Style this error message for user-facing display
      console.error('Failed to exchange code for token:', response.status);
      return null;
    }

    const data = await response.json();
    console.log(data);
    if (data.valid && data.access_token) {
      return {
        access_token: data.access_token,
        github_user_id: data.github_user_id,
        github_username: data.github_username
      };
    } else {
      // TODO: Style this error message for user-facing display
      console.error('Invalid response from backend:', data);
      return null;
    }
  } catch (error) {
    // TODO: Style this error message for user-facing display
    console.error('Error exchanging code for token:', error);
    return null;
  }
}

/**
 * Extracts the access token from the OAuth redirect URL
 * GitHub returns the token in the URL fragment or query parameters
 */
function extractTokenFromUrl(url) {
  try {
    const urlObj = new URL(url);

    // Check for token in URL fragment (implicit flow)
    if (urlObj.hash) {
      const params = new URLSearchParams(urlObj.hash.substring(1));
      const token = params.get('access_token');
      if (token) return token;
    }

    // Check for code in query params (authorization code flow)
    const code = urlObj.searchParams.get('code');
    if (code) {
      console.log('Received authorization code:', code);
      // Note: For authorization code flow, you'd need to exchange this code
      // for an access token via your backend. For now, we'll use implicit flow.
      return code;
    }

    return null;
  } catch (error) {
    console.error('Error extracting token from URL:', error);
    return null;
  }
}

/**
 * Stores the GitHub access token and user data in chrome.storage.local
 */
function storeGitHubToken(userData) {
  chrome.storage.local.set({
    githubToken: userData.access_token,
    github_user_id: userData.github_user_id,
    github_username: userData.github_username
  }, () => {
    if (chrome.runtime.lastError) {
      console.error('Error storing token:', chrome.runtime.lastError);
      alert('Failed to store GitHub token');
      return;
    }

    console.log('GitHub token and user data stored successfully');

    // Update UI to show signed-in state
    showSignedInView();
  });
}
