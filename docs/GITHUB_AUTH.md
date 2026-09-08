# GitHub authentication

Ghost Talent should not depend on GitHub's anonymous 60-request/hour REST quota for normal use.

## Maintainer setup (one time)

1. In GitHub, open **Settings → Developer settings → OAuth Apps → New OAuth App**.
2. Name the app `Ghost Talent`.
3. Use the project/repository URL as the homepage URL.
4. A callback URL may be set to `http://127.0.0.1:8765/`; Device Flow does not use the callback.
5. Create the OAuth App, then open its settings and **enable Device Flow**.
6. Copy the app's **Client ID** (not the client secret).
7. Put the Client ID in local `.env` while testing:

```env
GHOST_TALENT_GITHUB_CLIENT_ID=YOUR_PUBLIC_CLIENT_ID
```

The Client ID is public application metadata. Device Flow does **not** require a client secret, and Ghost Talent must never ship a GitHub client secret in this local/open-source application.

## User experience

After the maintainer Client ID is configured, normal users do not create or paste Personal Access Tokens:

1. Open **Settings → GitHub connection**.
2. Click **Connect GitHub**.
3. GitHub opens in the browser and shows an authorization page.
4. Enter the short code displayed by Ghost Talent and approve.
5. Ghost Talent stores the resulting user token locally under `~/.ghost-talent/github-auth.json` with restrictive file permissions where supported.
6. Settings shows the authenticated GitHub account and current REST API quota.

Authenticated user requests normally use the user's 5,000 requests/hour primary REST API limit. Anonymous public requests are only 60 requests/hour per originating IP.

## Developer fallback

`GITHUB_TOKEN` remains supported for development and CI. If it is present, it takes precedence over the locally connected account. Do not commit `.env`, access tokens, client secrets, or generated authorization files.
