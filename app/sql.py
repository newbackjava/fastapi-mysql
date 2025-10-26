# Raw SQL statements used by the app (centralized for clarity)
CREATE_TABLE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    age INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_USER = "INSERT INTO users (username, age) VALUES (%s, %s)"
SELECT_USERS = "SELECT id, username, age, created_at FROM users ORDER BY id DESC"
SELECT_USER_BY_ID = "SELECT id, username, age, created_at FROM users WHERE id=%s"
UPDATE_USER_BY_ID = "UPDATE users SET username=%s, age=%s WHERE id=%s"
DELETE_USER_BY_ID = "DELETE FROM users WHERE id=%s"
