# Uploads: files and images from users

*Last checked against vendor docs: October 2026. Storage product details change; confirm against current docs.*

## When to read this

Read before accepting any file or image from a user (profile picture, attachment, import, document), and before serving files back. Related: `abuse-controls.md` (rate limits), `access-control.md` (storage policies).

## Why this goes wrong

The easy implementation trusts what the browser says: the extension, the declared MIME type, the filename, the size shown in the form. All of that is chosen by the sender. The result is active content served from your own origin, stored files anyone can fetch or overwrite, and unbounded storage cost.

## Short version

1. **Size:** enforce a maximum on the server (and in the storage bucket or policy), not only in the browser.
2. **Type:** use an allowlist. Decide the type from the file's content (magic bytes, or decode and re-encode images), not from the extension or the client's `Content-Type`.
3. **No active content:** do not accept SVG, HTML, or scripts unless you sanitize them. Serve user files from a private bucket with signed URLs, as `Content-Disposition: attachment` where inline display is not needed, with a fixed content type and `X-Content-Type-Options: nosniff`.
4. **Names and paths:** generate the stored name (UUID); never use the client's filename in a path. Put each user's files under their own id prefix and enforce that in the storage policy.
5. **Access:** private by default. Reads and writes are limited to the owner by policy. Never a public-write bucket, never a `using (true)` policy, never the service key in client code.
6. **Images:** re-encode (this strips EXIF location and any payload), cap dimensions and pixel count.
7. **Cost and abuse:** per-user upload rate limit, per-user storage quota, delete old files when replaced or when the account is deleted.

## Implementation notes

- Check the signature: PDF starts with `%PDF-`, PNG with `89 50 4E 47`, JPEG with `FF D8 FF`, WebP with `RIFF....WEBP`. A library that decodes the file (an image library, a PDF parser) is stronger than comparing bytes.
- A client-side check (`accept=`, `file.type`, `file.size`) is for usability only.
- A bucket setting such as `allowed_mime_types` relies on the declared type. Keep it, but also verify content on a server path before storing, or re-encode after upload.
- Archives and office files: do not unpack or process them without limits on size, entry count and depth.
- Never pass a user filename to a shell or use it to build a path.

## Verify

- Upload a file larger than the limit: rejected on the server (call the endpoint directly, not through the form).
- Upload an `.html` or `.svg` file renamed to `.png`, or a PNG with a spoofed `Content-Type`: rejected or neutralised.
- A second user cannot read, overwrite or delete the first user's file by guessing the path.
- Stored name and path contain no client-supplied text.
- Downloads carry a fixed content type and `nosniff`.
- Search for `public: true` buckets, `using (true)` or `with check (true)` on storage objects, and service keys in client code.
