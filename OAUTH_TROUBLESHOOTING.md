# OAuth Token Troubleshooting Guide

This guide helps you resolve Google OAuth authentication issues with the Kanka to Markdown workflow.

## Quick Fix for Expired Tokens

If you see this error:
```
google.auth.exceptions.RefreshError: ('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})
```

**Solution:**
1. Run: `manage_oauth.bat clear`
2. Run: `manage_oauth.bat test`
3. Follow the browser authentication prompts

## Understanding OAuth Tokens

### What are OAuth Tokens?
- **Access Token**: Short-lived (1 hour) - used for API calls
- **Refresh Token**: Long-lived (can expire) - used to get new access tokens
- **Token File**: `token.pickle` - stores both tokens locally

### Why Do Tokens Expire?
- **Access tokens**: Expire every hour (automatically refreshed)
- **Refresh tokens**: Can expire due to:
  - Inactivity (6+ months)
  - Security policy changes
  - Google account changes
  - App permission changes

## Token Management Tools

### 1. Windows Batch Script (Recommended)
```bash
# Check token status
manage_oauth.bat status

# Clear expired token
manage_oauth.bat clear

# Test/authenticate
manage_oauth.bat test

# Show help
manage_oauth.bat help
```

### 2. Python Script Directly
```bash
# Check token status
python kanka_to_md/oauth_token_manager.py status

# Clear expired token
python kanka_to_md/oauth_token_manager.py clear

# Test/authenticate
python kanka_to_md/oauth_token_manager.py test
```

## Common Issues and Solutions

### Issue 1: "invalid_grant: Bad Request"
**Symptoms:**
- Token refresh fails
- OAuth authentication errors

**Solution:**
1. Clear the old token: `manage_oauth.bat clear`
2. Re-authenticate: `manage_oauth.bat test`
3. Follow browser prompts

### Issue 2: "OAuth credentials not found"
**Symptoms:**
- Missing `google/client_secret.json` file

**Solution:**
1. Ensure you have Google OAuth credentials
2. Place `client_secret.json` in the `google/` folder
3. See setup instructions in `SETUP_TEMPLATES.md`

### Issue 3: Browser doesn't open for authentication
**Symptoms:**
- No browser window opens during authentication

**Solution:**
1. Check if you have a default browser set
2. Try running the script manually: `python kanka_to_md/oauth_token_manager.py test`
3. Look for a localhost URL in the console output

### Issue 4: "Access denied" during authentication
**Symptoms:**
- Google shows "Access denied" page

**Solution:**
1. Check if your Google account has 2FA enabled
2. Ensure you're using the correct Google account
3. Check if the app is authorized in your Google account settings

## Automatic Token Handling

The improved `publish_to_drive_oauth.py` script now includes:

### ✅ Automatic Features
- **Token Validation**: Checks if token is valid before use
- **Token Refresh**: Automatically refreshes expired access tokens
- **Graceful Degradation**: Handles refresh failures gracefully
- **Clear Messaging**: Provides clear status messages
- **Automatic Re-auth**: Initiates OAuth flow when needed

### 🔄 What Happens Automatically
1. **Valid Token**: Uses existing token
2. **Expired Access Token**: Refreshes automatically
3. **Expired Refresh Token**: Clears old token and starts OAuth flow
4. **No Token**: Starts OAuth flow immediately

## Manual Token Management

### Check Token Status
```bash
manage_oauth.bat status
```
**Exit Codes:**
- `0`: Token is valid
- `1`: Token is expired but refreshable
- `2`: No token or invalid token

### Clear Token
```bash
manage_oauth.bat clear
```
- Removes `token.pickle` file
- Forces re-authentication on next run

### Test Authentication
```bash
manage_oauth.bat test
```
- Tests current token
- Refreshes if needed
- Starts OAuth flow if necessary

## Prevention Tips

### 1. Regular Usage
- Use the workflow regularly (tokens last longer with active use)
- Run at least once every 6 months to keep tokens fresh

### 2. Monitor Token Status
- Check token status before important runs: `manage_oauth.bat status`
- Clear tokens proactively if you haven't used them in months

### 3. Keep Credentials Updated
- Ensure `google/client_secret.json` is current
- Update OAuth app settings in Google Cloud Console if needed

## File Locations

### Token Files
- **Token File**: `token.pickle` (in project root)
- **File ID**: `drive_file_id_oauth.json` (stores Google Drive file ID)
- **Credentials**: `google/client_secret.json` (OAuth app credentials)

### Log Files
- **Main Log**: `logs/realmpress.log`
- **OAuth Logs**: Console output during authentication

## Getting Help

If you continue to have issues:

1. **Check the logs**: Look at `logs/realmpress.log` for detailed error messages
2. **Verify credentials**: Ensure `google/client_secret.json` is properly configured
3. **Test manually**: Use `manage_oauth.bat test` to isolate the issue
4. **Check Google account**: Ensure your Google account allows OAuth apps

## Security Notes

- **Token files** contain sensitive authentication data
- **Never commit** `token.pickle` or `client_secret.json` to version control
- **Keep credentials** secure and don't share them
- **Revoke access** in Google account settings if needed

---

**Remember**: The improved OAuth handling should prevent most token issues automatically. If you still encounter problems, the manual tools above will help you resolve them quickly.
