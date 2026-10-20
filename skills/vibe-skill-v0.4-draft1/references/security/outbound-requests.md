# Outbound requests: your server fetching an address a user supplied

*Last checked against vendor docs: October 2026. Library details change; confirm against current docs.*

## When to read this

Read before writing code that makes your server request a URL, host or IP that came from a user: link previews, import-from-URL, image or avatar-from-URL, RSS or feed readers, webhooks a user configures, "test this endpoint" buttons, proxies.

## Why this goes wrong

The server sits inside your network and next to your cloud's metadata service. A user who can choose the address can make the server read internal services, `localhost`, and cloud credentials (`169.254.169.254`), or use it to attack others. Checking the hostname text is not enough: a name can resolve to a private IP, a public URL can redirect to one, and DNS can change between check and use.

## Rules

1. **Authenticate and limit.** Require a signed-in user; add a per-user rate limit and a global ceiling (see `abuse-controls.md`).
2. **Allow only `http:` and `https:`**, default ports unless you have a reason, no credentials in the URL.
3. **Resolve, then check the IP.** Resolve the host yourself and refuse loopback, private (`10/8`, `172.16/12`, `192.168/16`), link-local (`169.254/16`, including the metadata address), carrier-grade NAT (`100.64/10`), unspecified, multicast, and the IPv6 equivalents (`::1`, `fc00::/7`, `fe80::/10`, IPv4-mapped addresses). Connect to the IP you checked (pin it), so DNS cannot change in between.
4. **Redirects:** disable them, or follow manually, at most 3 hops, and run steps 2 and 3 again on every hop.
5. **Bound the work:** a connect and total timeout (a few seconds), a response size cap enforced while streaming, a content-type allowlist for what you expect, no cookies or your own auth headers forwarded.
6. **Treat the response as untrusted.** Store and render it as text, escape it, never render fetched HTML or scripts, and do not hot-link fetched image URLs without validating them.
7. **Webhooks:** apply the same checks at send time (not only when the URL is saved), sign the payload, set a timeout so a slow target cannot block the user's request, and let only the owner set or read their URL.
8. Prefer a vetted SSRF-safe HTTP client or an egress proxy over hand-rolling the IP checks, if one exists for the stack.

```ts
// Sketch: resolve, check, pin. Reuse for every redirect hop.
const addrs = await dns.lookup(url.hostname, { all: true });
if (addrs.some(a => isPrivateOrReserved(a.address))) throw new Error("blocked");
// connect to addrs[0].address with Host/SNI set to url.hostname
```

## Verify

- Requests to `http://127.0.0.1`, `http://localhost`, `http://169.254.169.254`, a name that resolves to a private IP, and a public URL that redirects to one are all refused.
- A very large or very slow response is cut off.
- The route refuses anonymous callers.
