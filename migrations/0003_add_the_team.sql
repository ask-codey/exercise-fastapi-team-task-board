-- Migration 3: the practice team and their four tasks, so you can sign in on the docs page and the tests start from
-- the same rows. Each password is stored as its Argon2 hash, made with pwdlib, never as the password itself. The
-- practice passwords are practice-maya, practice-theo and practice-sofia.
INSERT INTO users (id, name, email, password_hash, role) VALUES
    (1, 'Maya', 'maya@example.com',
     '$argon2id$v=19$m=65536,t=3,p=4$DmXX85gutVE1KWyvzs9OrA$DazSOlbhfOGWzib7eClELT1t6acDYlc7zQSwwx2X8tY', 'admin'),
    (2, 'Theo', 'theo@example.com',
     '$argon2id$v=19$m=65536,t=3,p=4$0iVjvFmdIShtEpEddmaQSQ$FDziIfDNGtLZ3AXTQFxOQZK0oP9s15qI0KXUc+xFv0U', 'member'),
    (3, 'Sofia', 'sofia@example.com',
     '$argon2id$v=19$m=65536,t=3,p=4$1Vc1eiqrWyq20yGlK1MKNA$GAdgAWM10LHm09J8Jxcqm0OhrA61dazoLur7TRijz3g', 'member');

INSERT INTO tasks (id, title, owner_id, done) VALUES
    (1, 'Book the room for the sprint demo', 1, 0),
    (2, 'Write the release notes', 2, 0),
    (3, 'Fix the typo on the sign-in page', 3, 1),
    (4, 'Order new whiteboard markers', 2, 0);
