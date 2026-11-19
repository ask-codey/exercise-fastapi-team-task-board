-- Migration 1: the users table, one row for each person on the team.
--   id             a whole number SQLite gives each new user (INTEGER PRIMARY KEY)
--   name           the person's first name: text, never missing
--   email          what they sign in with: text, never missing, and no two users share one (UNIQUE)
--   password_hash  the Argon2 hash of their password, made with pwdlib: never the password itself
--   role           what kind of user they are: 'member' or 'admin', never missing
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('member', 'admin'))
);
