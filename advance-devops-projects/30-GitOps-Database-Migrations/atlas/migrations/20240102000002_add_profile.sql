ALTER TABLE users ADD COLUMN display_name TEXT;
CREATE TABLE profiles (user_id INT REFERENCES users(id), bio TEXT);
