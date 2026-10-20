const Database = require("better-sqlite3");
const db = new Database(process.env.DB_FILE || "notes.db");
db.pragma("journal_mode = WAL");
db.exec(`
  create table if not exists users (
    id integer primary key autoincrement,
    email text not null unique,
    password_hash text not null,
    created_at text not null default (datetime('now'))
  );
  create table if not exists notes (
    id integer primary key autoincrement,
    user_id integer not null references users(id) on delete cascade,
    title text not null,
    body text not null default '',
    tag text,
    created_at text not null default (datetime('now'))
  );
`);
module.exports = db;
