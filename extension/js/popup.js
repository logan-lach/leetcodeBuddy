// Configuration
const GITHUB_CLIENT_ID = 'YOUR_GITHUB_CLIENT_ID'; // Replace with your GitHub OAuth App Client ID
const BACKEND_URL = 'http://localhost:5000'; // Update for production
const REDIRECT_URI = chrome.identity.getRedirectURL('oauth');

// Sign in with GitHub button handler
document.getElementById("githubSignIn").addEventListener("click", async () => {
  console.log("Sign in with GitHub clicked");

  try {
    // Generate random state for CSRF protection
    const state = generateRandomState();

    // Build GitHub OAuth URL
    const authUrl = new URL('https://github.com/login/oauth/authorize');
    authUrl.searchParams.set('client_id', GITHUB_CLIENT_ID);
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.set('scope', 'repo user');
    authUrl.searchParams.set('state', state);

    // Launch OAuth flow in browser
    const redirectUrl = await chrome.identity.launchWebAuthFlow({
      url: authUrl.toString(),
      interactive: true
    });

    // Extract authorization code from redirect URL
    const url = new URL(redirectUrl);
    const code = url.searchParams.get('code');
    const returnedState = url.searchParams.get('state');

    // Verify state for CSRF protection
    if (returnedState !== state) {
      throw new Error('State mismatch - potential CSRF attack');
    }

    if (!code) {
      throw new Error('No authorization code received from GitHub');
    }

    // Send authorization code to backend
    const response = await fetch(`${BACKEND_URL}/api/github/authorize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Authorization failed');
    }

    const data = await response.json();

    // Store session token in chrome.storage
    await chrome.storage.local.set({
      sessionToken: data.session_token,
      githubUsername: data.user.username,
      githubEmail: data.user.email
    });

    console.log('Successfully authenticated:', data.user.username);
    alert(`Successfully signed in as ${data.user.username}!`);

    // TODO: Update UI to show signed-in state

  } catch (error) {
    console.error('GitHub OAuth error:', error);
    alert(`Sign-in failed: ${error.message}`);
  }
});

// Helper function to generate random state for CSRF protection
function generateRandomState() {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}
