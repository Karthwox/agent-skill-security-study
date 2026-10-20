const express = require("express");
const bcrypt = require("bcryptjs");
const db = require("./db");
const { sign, requireAuth } = require("./auth");

const app = express();
app.use(express.json({ limit: "100kb" }));

app.post("/register", (req, res) => {
  const { email, password } = req.body || {};
  if (typeof email !== "string" || typeof password !== "string" || password.length < 8) {
    return res.status(400).json({ error: "invalid input" });
  }
  try {
    const hash = bcrypt.hashSync(password, 12);
    const info = db.prepare("insert into users (email, password_hash) values (?, ?)").run(email.toLowerCase(), hash);
    res.status(201).json({ token: sign({ id: info.lastInsertRowid }) });
  } catch {
    res.status(400).json({ error: "could not register" });
  }
});

app.post("/login", (req, res) => {
  const { email, password } = req.body || {};
  const user = typeof email === "string" ? db.prepare("select * from users where email = ?").get(email.toLowerCase()) : null;
  if (!user || typeof password !== "string" || !bcrypt.compareSync(password, user.password_hash)) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  res.json({ token: sign(user) });
});

app.get("/notes", requireAuth, (req, res) => {
  res.json(db.prepare("select id, title, body, tag, created_at from notes where user_id = ? order by id desc").all(req.userId));
});

app.post("/notes", requireAuth, (req, res) => {
  const { title, body, tag } = req.body || {};
  if (typeof title !== "string" || !title) return res.status(400).json({ error: "title required" });
  const info = db.prepare("insert into notes (user_id, title, body, tag) values (?, ?, ?, ?)")
    .run(req.userId, title, typeof body === "string" ? body : "", typeof tag === "string" ? tag : null);
  res.status(201).json({ id: info.lastInsertRowid });
});

app.delete("/notes/:id", requireAuth, (req, res) => {
  db.prepare("delete from notes where id = ? and user_id = ?").run(req.params.id, req.userId);
  res.status(204).end();
});

app.listen(process.env.PORT || 3000);
