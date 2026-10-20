const express = require("express");
const crypto = require("node:crypto");

const app = express();
app.use(express.json({ limit: "100kb" }));

const users = new Map();     // email -> { id, hash, salt }
const sessions = new Map();  // session id -> user id
const notes = [];            // { id, userId, title, body }

function hashPassword(password, salt) {
  return crypto.scryptSync(password, salt, 64).toString("hex");
}

function parseCookies(header = "") {
  return Object.fromEntries(header.split(";").map((c) => c.trim().split("=")).filter((p) => p[0]));
}

function auth(req, res, next) {
  const sid = parseCookies(req.headers.cookie).sid;
  const userId = sid && sessions.get(sid);
  if (!userId) return res.status(401).json({ error: "Not signed in" });
  req.userId = userId;
  next();
}

app.post("/signup", (req, res) => {
  const { email, password } = req.body ?? {};
  if (typeof email !== "string" || typeof password !== "string" || password.length < 8) {
    return res.status(400).json({ error: "Email and a password of at least 8 characters are required" });
  }
  if (users.has(email)) return res.status(409).json({ error: "Account exists" });
  const salt = crypto.randomBytes(16).toString("hex");
  users.set(email, { id: crypto.randomUUID(), salt, hash: hashPassword(password, salt) });
  res.status(201).json({ ok: true });
});

app.post("/login", (req, res) => {
  const { email, password } = req.body ?? {};
  const user = users.get(email);
  if (!user || hashPassword(String(password), user.salt) !== user.hash) {
    return res.status(401).json({ error: "Invalid email or password" });
  }
  const sid = crypto.randomBytes(32).toString("hex");
  sessions.set(sid, user.id);
  res.setHeader("Set-Cookie", `sid=${sid}; HttpOnly; SameSite=Lax; Path=/`);
  res.json({ ok: true });
});

app.post("/logout", auth, (req, res) => {
  const sid = parseCookies(req.headers.cookie).sid;
  sessions.delete(sid);
  res.setHeader("Set-Cookie", "sid=; Max-Age=0; Path=/");
  res.json({ ok: true });
});

app.get("/notes", auth, (req, res) => {
  res.json(notes.filter((n) => n.userId === req.userId).map(({ id, title, body }) => ({ id, title, body })));
});

app.post("/notes", auth, (req, res) => {
  const { title, body } = req.body ?? {};
  if (typeof title !== "string" || !title.trim() || title.length > 200) return res.status(400).json({ error: "Invalid title" });
  const note = { id: crypto.randomUUID(), userId: req.userId, title, body: typeof body === "string" ? body.slice(0, 20000) : "" };
  notes.push(note);
  res.status(201).json({ id: note.id, title: note.title, body: note.body });
});

app.delete("/notes/:id", auth, (req, res) => {
  const i = notes.findIndex((n) => n.id === req.params.id && n.userId === req.userId);
  if (i < 0) return res.status(404).json({ error: "Not found" });
  notes.splice(i, 1);
  res.status(204).end();
});

const port = process.env.PORT || 4000;
app.listen(port, () => console.log(`API on http://localhost:${port}`));
