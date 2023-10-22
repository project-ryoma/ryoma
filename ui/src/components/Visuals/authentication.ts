import { PublicClientApplication } from '@azure/msal-browser';

// MSAL configuration
const msalConfig = {
  auth: {
    clientId: 'your-client-id',  // Your Azure AD app client ID
    authority: 'https://login.microsoftonline.com/your-tenant-id',  // Your Azure AD tenant ID
    redirectUri: window.location.origin,
  },
};

const msalInstance = new PublicClientApplication(msalConfig);

export async function authenticate(): Promise<string> {
  try {
    // Attempt to acquire token silently
    const silentResult = await msalInstance.acquireTokenSilent({
      scopes: ['user.read'],  // Replace with your own scopes
    });
    return silentResult.accessToken;
  } catch (silentError) {
    // If silent token acquisition fails, attempt interactive token acquisition
    try {
      const interactiveResult = await msalInstance.acquireTokenPopup({
        scopes: ['user.read'],  // Replace with your own scopes
      });
      return interactiveResult.accessToken;
    } catch (interactiveError) {
      console.error('Interactive token acquisition failed:', interactiveError);
      throw interactiveError;
    }
  }
}
