# Cross-origin setups: separate web and API hosts, shared cookies, embedding

*Last checked against vendor docs: October 2026. Browser cookie rules change; confirm against current docs.*

## When to read this

Read when the browser app and the API run on different origins (different host, subdomain or port), when a cookie is shared across hosts, when another site must call your API from the browser or embed your pages, or when you add CORS headers.

## Why this goes wrong

The quick fix for "the browser blocked my request" is to allow every origin, add credentials, and loosen cookie flags. That turns the browser into a tool for any other website to act as the signed-in user. Sibling subdomains are the same site, so `SameSite` does not stop requests from one to another.

## Rules

1. **CORS: one exact origin.** Allow only the exact web origin from configuration (scheme, host and port). Never `*`, never echo back the request's `Origin`, and never allow credentials with a wildcard. Development origins come from development configuration only. Cross-origin access is for the origins the task named; do not extend it to others.
2. **CSRF protection on every state-changing route that uses cookie authentication.** Check the `Origin` (or `Referer`) header against the allowed origin and reject mismatches, and for requests with no `Origin`, require a custom header or a CSRF token. `SameSite` alone does not count.
3. **Cookies:** `HttpOnly`, `Secure` in production, `SameSite=Lax` by default. Use `SameSite=None` only when a different site truly needs the cookie, and then say why and what it costs. Scope the `Domain` deliberately (host-only is safest). Never remove a flag the project already sets.
4. **Errors:** the API must not return stack traces or internals in production. Add an error handler that returns a generic message, log the detail on the server, and make sure production mode is actually set (`NODE_ENV=production` in the start script or host settings), because defaults often leak.
5. **Headers:** `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, and `frame-ancestors` (or `X-Frame-Options`) listing only who may embed you. Redirect HTTP to HTTPS and never disable certificate verification.
6. **Embedding or partner access:** prefer a read-only endpoint scoped to the signed-in user, an exact partner origin, and no write access for the partner unless asked.

## Verify

- A request from another origin gets no CORS headers, and a credentialed preflight from an unlisted origin fails.
- A state-changing request with a forged `Origin` (and none) is rejected.
- Cookie flags in the response match the list above.
- A malformed request body in production mode returns a generic error with no stack trace.
